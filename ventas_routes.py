from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Producto, Venta, DetalleVenta
from datetime import datetime
from decimal import Decimal

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
@login_required
def listar():
    ventas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    return render_template('ventas.html', ventas=ventas)

@ventas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            productos_json = request.form.get('productos_json')
            observaciones = request.form.get('observaciones')
            
            if not productos_json:
                flash('Debe seleccionar al menos un producto.', 'warning')
                return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
            
            import json
            productos_data = json.loads(productos_json)
            
            if not productos_data:
                flash('Debe seleccionar al menos un producto.', 'warning')
                return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
            
            # Validar y procesar productos
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
                    return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
                
                cantidad = int(cantidad)
                
                if cantidad <= 0:
                    flash(f'La cantidad para {producto.nombre} debe ser mayor a cero.', 'warning')
                    return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
                
                if cantidad > producto.stock_actual:
                    flash(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {cantidad}', 'danger')
                    return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
                
                subtotal = producto.precio_venta * cantidad
                total += subtotal
                
                detalles.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio_venta,
                    'subtotal': subtotal
                })
            
            if not detalles:
                flash('No se agregaron productos válidos a la venta.', 'warning')
                return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
            
            # Crear venta
            venta = Venta(
                usuario_id=current_user.id,
                total=total,
                observaciones=observaciones,
                estado='confirmada'
            )
            
            db.session.add(venta)
            db.session.flush()  # Para obtener el ID de la venta
            
            # Crear detalles y descontar stock
            for detalle in detalles:
                detalle_venta = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=detalle['producto'].id,
                    cantidad=detalle['cantidad'],
                    precio_unitario=detalle['precio_unitario'],
                    subtotal=detalle['subtotal']
                )
                db.session.add(detalle_venta)
                
                # Descontar stock
                detalle['producto'].stock_actual -= detalle['cantidad']
            
            db.session.commit()
            
            flash(f'Venta creada exitosamente. Total: ${total:.2f}', 'success')
            return redirect(url_for('ventas.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la venta: {str(e)}', 'danger')
            return render_template('venta_form.html', productos=Producto.query.filter_by(activo=True).all())
    
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('venta_form.html', productos=productos)

@ventas_bp.route('/anular/<int:id>', methods=['POST'])
@login_required
def anular(id):
    venta = Venta.query.get_or_404(id)
    
    if venta.estado == 'anulada':
        flash('Esta venta ya está anulada.', 'warning')
        return redirect(url_for('ventas.listar'))
    
    if current_user.rol != 'administrador' and venta.usuario_id != current_user.id:
        flash('No tienes permiso para anular esta venta.', 'danger')
        return redirect(url_for('ventas.listar'))
    
    try:
        # Revertir stock de cada producto
        for detalle in venta.detalles:
            producto = Producto.query.get(detalle.producto_id)
            if producto:
                producto.stock_actual += detalle.cantidad
        
        # Cambiar estado de la venta
        venta.estado = 'anulada'
        
        db.session.commit()
        flash('Venta anulada exitosamente. Stock revertido.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al anular la venta: {str(e)}', 'danger')
    
    return redirect(url_for('ventas.listar'))

@ventas_bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    venta = Venta.query.get_or_404(id)
    return render_template('venta_detalle.html', venta=venta)

@ventas_bp.route('/api/productos-disponibles')
@login_required
def api_productos_disponibles():
    productos = Producto.query.filter_by(activo=True).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'stock_actual': p.stock_actual,
        'precio_venta': float(p.precio_venta)
    } for p in productos])
