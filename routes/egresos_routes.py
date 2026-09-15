from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Egreso, Producto
from datetime import datetime
from decimal import Decimal
from utils.seguridad import rol_requerido
import json

egresos_bp = Blueprint('egresos', __name__, url_prefix='/gastos')

@egresos_bp.route('/')
@login_required
@rol_requerido('administrador')
def listar():
    # RN-07: Solo mostrar egresos activos
    egresos = Egreso.query.filter_by(activo=True).order_by(Egreso.fecha_hora.desc()).all()
    return render_template('egresos.html', egresos=egresos)

@egresos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('administrador')
def crear_egreso():
    # Verificar si viene del botón "Reabastecer" del dashboard
    reabastecer_producto_id = request.args.get('reabastecer_producto')
    producto_reabastecer = None
    
    if reabastecer_producto_id:
        producto_reabastecer = Producto.query.get(int(reabastecer_producto_id))
    
    if request.method == 'POST':
        try:
            print("DEBUG: Recibiendo POST para crear egreso")
            print("DEBUG: Form data:", dict(request.form))
            
            tipo_gasto = request.form.get('tipo_gasto')
            descripcion = request.form.get('descripcion')
            observaciones = request.form.get('observaciones')
            otro_detalle = request.form.get('otro_detalle')
            
            print(f"DEBUG: Tipo de gasto: {tipo_gasto}")
            print(f"DEBUG: Descripción: {descripcion}")
            
            # Determinar categoría basada en el tipo de gasto
            categoria_map = {
                'servicios_publicos': 'Servicios públicos',
                'arriendo': 'Arriendo',
                'nomina': 'Nómina',
                'compra_insumos': 'Compra de insumos',
                'otro': otro_detalle or 'Otro'
            }
            categoria = categoria_map.get(tipo_gasto, 'Otro')
            
            if tipo_gasto == 'compra_insumos':
                print("DEBUG: Procesando compra de insumos")
                # Procesar compra de insumos
                productos_json = request.form.get('productos_json')
                print(f"DEBUG: Productos JSON recibido: {productos_json}")
                
                if not productos_json:
                    flash('No hay productos en la compra de insumos.', 'warning')
                    return render_template('egreso_form.html', action='crear')
                
                productos = json.loads(productos_json)
                print(f"DEBUG: Productos parseados: {productos}")
                monto_total = Decimal('0')
                
                for prod in productos:
                    cantidad = int(prod['cantidad'])
                    costo_unitario = Decimal(str(prod['precio_costo']))
                    
                    # Verificar si es un producto nuevo
                    es_nuevo = prod.get('es_nuevo_producto', False)
                    
                    if es_nuevo:
                        print(f"DEBUG: Creando nuevo producto: {prod['nombre']}")
                        # Crear el producto nuevo en la base de datos
                        nuevo_producto = Producto(
                            nombre=prod['nombre'],
                            descripcion='',
                            precio_costo=costo_unitario,
                            precio_venta=Decimal(str(prod.get('precio_venta', costo_unitario))),
                            stock_actual=cantidad,
                            stock_minimo=int(prod.get('stock_minimo', 5))
                        )
                        db.session.add(nuevo_producto)
                        db.session.flush()  # Para obtener el ID sin hacer commit todavía
                        
                        # Actualizar el producto_id en el array para referencia
                        prod['producto_id'] = nuevo_producto.id
                        producto = nuevo_producto
                    else:
                        # Producto existente
                        producto_id = prod['producto_id']
                        print(f"DEBUG: Procesando producto existente ID {producto_id}, cantidad {cantidad}, costo {costo_unitario}")
                        
                        # Buscar el producto
                        producto = Producto.query.get(producto_id)
                        if not producto:
                            flash(f'Producto con ID {producto_id} no encontrado.', 'danger')
                            return render_template('egreso_form.html', action='crear')
                        
                        # Sumar cantidad al stock
                        producto.stock_actual += cantidad
                        
                        # Actualizar precio_costo si es diferente
                        if producto.precio_costo != costo_unitario:
                            producto.precio_costo = costo_unitario
                    
                    # Sumar al monto total
                    monto_total += costo_unitario * cantidad
                
                # Usar la descripción generada automáticamente
                if not descripcion:
                    productos_texto = ', '.join([f"{p['cantidad']} {p['nombre']}" for p in productos])
                    descripcion = f"Compra de insumos: {productos_texto}"
                
                print(f"DEBUG: Monto total: {monto_total}")
                print(f"DEBUG: Descripción final: {descripcion}")
                
                egreso = Egreso(
                    descripcion=descripcion,
                    monto=monto_total,
                    categoria=categoria,
                    observaciones=observaciones,
                    usuario_id=current_user.id,
                    activo=True,
                    productos_json=json.dumps(productos)  # Guardar con los IDs actualizados
                )
                
                db.session.add(egreso)
                db.session.commit()
                
                print("DEBUG: Egreso creado exitosamente")
                flash('Compra de insumos registrada exitosamente. Stock actualizado.', 'success')
                return redirect(url_for('egresos.listar'))
                
            else:
                print("DEBUG: Procesando gasto normal")
                # Gasto normal (servicios, arriendo, nómina, otro)
                monto = Decimal(request.form.get('monto'))
                
                if not descripcion:
                    flash('La descripción es obligatoria.', 'warning')
                    return render_template('egreso_form.html', action='crear')
                
                if monto <= 0:
                    flash('El monto debe ser mayor a cero.', 'warning')
                    return render_template('egreso_form.html', action='crear')
                
                egreso = Egreso(
                    descripcion=descripcion,
                    monto=monto,
                    categoria=categoria,
                    observaciones=observaciones,
                    usuario_id=current_user.id,
                    activo=True
                )
                
                db.session.add(egreso)
                db.session.commit()
                
                flash('Gasto registrado exitosamente.', 'success')
                return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            print(f"DEBUG: Error al registrar gasto: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash(f'Error al registrar el gasto: {str(e)}', 'danger')
            return render_template('egreso_form.html', action='crear')
    
    return render_template('egreso_form.html', action='crear', producto_reabastecer=producto_reabastecer)

@egresos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('administrador')
def editar_egreso(id):
    egreso = Egreso.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            egreso.descripcion = request.form.get('descripcion')
            egreso.monto = Decimal(request.form.get('monto'))
            egreso.categoria = request.form.get('categoria')
            egreso.observaciones = request.form.get('observaciones')
            
            if not egreso.descripcion:
                flash('La descripción es obligatoria.', 'warning')
                return render_template('egreso_form.html', egreso=egreso, action='editar')
            
            if egreso.monto <= 0:
                flash('El monto debe ser mayor a cero.', 'warning')
                return render_template('egreso_form.html', egreso=egreso, action='editar')
            
            db.session.commit()
            flash('Gasto actualizado exitosamente.', 'success')
            return redirect(url_for('egresos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el gasto: {str(e)}', 'danger')
            return render_template('egreso_form.html', egreso=egreso, action='editar')
    
    return render_template('egreso_form.html', egreso=egreso, action='editar')

@egresos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@rol_requerido('administrador')
def eliminar_egreso(id):
    egreso = Egreso.query.get_or_404(id)
    
    try:
        # RN-07: Eliminación lógica en lugar de física
        egreso.activo = False
        db.session.commit()
        flash('Gasto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el gasto: {str(e)}', 'danger')
    
    return redirect(url_for('egresos.listar'))
