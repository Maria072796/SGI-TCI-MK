from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Producto, Venta, DetalleVenta, CierreCaja
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
@login_required
def listar():
    """Lista ventas según el rol del usuario (RN-04)"""
    if current_user.rol == 'vendedor':
        # Vendedor solo ve sus propias ventas
        ventas = Venta.query.filter_by(usuario_id=current_user.id).order_by(Venta.fecha_hora.desc()).all()
    else:
        # Administrador ve todas las ventas
        ventas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    
    return render_template('ventas.html', ventas=ventas)

@ventas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crea una nueva venta siguiendo las reglas de negocio RN-03, RN-04, RN-05, RN-06"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            productos_json = request.form.get('productos_json')
            observaciones = request.form.get('observaciones')
            
            if not productos_json:
                flash('Agrega al menos un producto para confirmar la venta.', 'warning')
                return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
            
            import json
            productos_data = json.loads(productos_json)
            
            if not productos_data:
                flash('Agrega al menos un producto para confirmar la venta.', 'warning')
                return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
            
            # Validar y procesar productos según RN-03 y RN-05
            detalles = []
            total = Decimal('0')
            
            for item in productos_data:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad', 1)
                
                if not producto_id:
                    continue
                    
                producto = Producto.query.get(int(producto_id))
                if not producto:
                    flash(f'Producto con ID {producto_id} no encontrado.', 'danger')
                    return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
                
                cantidad = int(cantidad)
                
                if cantidad <= 0:
                    flash(f'La cantidad para {producto.nombre} debe ser mayor a cero.', 'warning')
                    return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
                
                # RN-05: Validar stock antes de confirmar
                if cantidad > producto.stock_actual:
                    flash(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {cantidad}', 'danger')
                    return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
                
                subtotal = producto.precio_venta * cantidad
                total += subtotal
                
                detalles.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio_venta,
                    'costo_unitario': producto.precio_costo,  # Guardar costo vigente (RN-10)
                    'subtotal': subtotal
                })
            
            if not detalles:
                flash('No se agregaron productos válidos a la venta.', 'warning')
                return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
            
            # RN-04: Asociar venta al usuario autenticado
            venta = Venta(
                usuario_id=current_user.id,
                total=total,
                observaciones=observaciones,
                estado='confirmada'
            )
            
            db.session.add(venta)
            db.session.flush()  # Para obtener el ID de la venta
            
            # Crear detalles con costo_unitario y descontar stock (RN-05, RN-06)
            for detalle in detalles:
                detalle_venta = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=detalle['producto'].id,
                    cantidad=detalle['cantidad'],
                    precio_unitario=detalle['precio_unitario'],
                    costo_unitario=detalle['costo_unitario'],  # RN-10: costo al momento de venta
                    subtotal=detalle['subtotal']
                )
                db.session.add(detalle_venta)
                
                # RN-05: Descontar stock en la misma transacción
                detalle['producto'].stock_actual -= detalle['cantidad']
            
            db.session.commit()
            
            flash(f'Registramos la venta #{venta.id} por ${total:.2f}', 'success')
            return redirect(url_for('ventas.detalle', id=venta.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la venta: {str(e)}', 'danger')
            return render_template('venta_form_v4.html', productos=Producto.query.filter_by(activo=True).all())
    
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('venta_form_v4.html', productos=productos)

@ventas_bp.route('/anular/<int:id>', methods=['POST'])
@login_required
def anular(id):
    """Anula una venta según RN-08"""
    venta = Venta.query.get_or_404(id)
    
    if venta.estado == 'anulada':
        flash('Esta venta ya está anulada.', 'warning')
        return redirect(url_for('ventas.listar'))
    
    # RN-08: Validar permisos
    if current_user.rol == 'vendedor':
        # Vendedor solo puede anular sus propias ventas del día
        if venta.usuario_id != current_user.id:
            flash('No tienes permiso para anular esta venta.', 'danger')
            return redirect(url_for('ventas.listar'))
        
        # Verificar que sea del día actual
        if venta.fecha_hora.date() != date.today():
            flash('Solo puedes anular ventas del día actual.', 'warning')
            return redirect(url_for('ventas.listar'))
        
        # Verificar que no esté incluida en un cierre de turno
        cierre_existente = CierreCaja.query.filter_by(
            fecha=venta.fecha_hora.date(),
            usuario_id=current_user.id,
            tipo='turno'
        ).first()
        
        if cierre_existente:
            flash('Esta venta ya fue incluida en tu cierre de turno; pídele a la administradora que la anule.', 'warning')
            return redirect(url_for('ventas.listar'))
    
    motivo = request.form.get('motivo', '')
    
    try:
        # RN-08: Revertir stock de cada producto
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                producto.stock_actual += detalle.cantidad
        
        # RN-08: Cambiar estado y registrar información de anulación
        venta.estado = 'anulada'
        venta.fecha_anulacion = datetime.utcnow()
        venta.anulada_por = current_user.id
        venta.motivo_anulacion = motivo
        
        db.session.commit()
        flash(f'Anulamos la venta #{venta.id}. Los productos vuelven al inventario.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al anular la venta: {str(e)}', 'danger')
    
    return redirect(url_for('ventas.detalle', id=id))

@ventas_bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    venta = Venta.query.get_or_404(id)
    return render_template('venta_detalle.html', venta=venta)

# Ruta adicional para el nuevo naming de la v4
@ventas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def crear_venta():
    """Alias para crear() para mantener compatibilidad con v4"""
    return crear()

@ventas_bp.route('/api/productos-disponibles')
@login_required
def api_productos_disponibles():
    """API para el autocompletado de productos (solo activos con stock > 0 según RN-05)"""
    productos = Producto.query.filter_by(activo=True).filter(Producto.stock_actual > 0).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'stock_actual': p.stock_actual,
        'precio_venta': float(p.precio_venta),
        'precio_costo': float(p.precio_costo)
    } for p in productos])
