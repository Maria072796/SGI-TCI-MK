from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Producto
from decimal import Decimal
from utils.seguridad import rol_requerido
from flask import current_app as app  # Para acceder al decorador

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
@login_required
def listar():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para acceder al inventario.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    productos = Producto.query.filter_by(activo=True).all()
    
    # Calcular valor total del inventario
    valor_total_inventario = sum(p.stock_actual * float(p.precio_costo) for p in productos)
    
    # Calcular productos con stock bajo
    productos_bajo_stock = [p for p in productos if p.stock_actual <= p.stock_minimo]
    
    return render_template('inventario.html', productos=productos, valor_total_inventario=valor_total_inventario, productos_bajo_stock=productos_bajo_stock)

@inventario_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('administrador')
def crear():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para crear productos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            precio_costo = Decimal(request.form.get('precio_costo'))
            precio_venta = Decimal(request.form.get('precio_venta'))
            stock_actual = int(request.form.get('stock_actual', 0))
            stock_minimo = int(request.form.get('stock_minimo', 0))
            
            if not nombre:
                flash('El nombre del producto es obligatorio.', 'warning')
                return render_template('inventario_form.html', action='crear')
            
            if precio_costo <= 0 or precio_venta <= 0:
                flash('Los precios deben ser mayores a cero.', 'warning')
                return render_template('inventario_form.html', action='crear')
            
            if stock_actual < 0 or stock_minimo < 0:
                flash('El stock no puede ser negativo.', 'warning')
                return render_template('inventario_form.html', action='crear')
            
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio_costo=precio_costo,
                precio_venta=precio_venta,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo
            )
            
            db.session.add(producto)
            db.session.commit()
            
            flash('Producto creado exitosamente.', 'success')
            return redirect(url_for('inventario.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el producto: {str(e)}', 'danger')
            return render_template('inventario_form.html', action='crear')
    
    return render_template('inventario_form.html', action='crear')

@inventario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('administrador')
def editar(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para editar productos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            producto.nombre = request.form.get('nombre')
            producto.descripcion = request.form.get('descripcion')
            producto.precio_costo = Decimal(request.form.get('precio_costo'))
            producto.precio_venta = Decimal(request.form.get('precio_venta'))
            producto.stock_actual = int(request.form.get('stock_actual', 0))
            producto.stock_minimo = int(request.form.get('stock_minimo', 0))
            
            if not producto.nombre:
                flash('El nombre del producto es obligatorio.', 'warning')
                return render_template('inventario_form.html', producto=producto, action='editar')
            
            if producto.precio_costo <= 0 or producto.precio_venta <= 0:
                flash('Los precios deben ser mayores a cero.', 'warning')
                return render_template('inventario_form.html', producto=producto, action='editar')
            
            if producto.stock_actual < 0 or producto.stock_minimo < 0:
                flash('El stock no puede ser negativo.', 'warning')
                return render_template('inventario_form.html', producto=producto, action='editar')
            
            db.session.commit()
            flash('Producto actualizado exitosamente.', 'success')
            return redirect(url_for('inventario.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'danger')
            return render_template('inventario_form.html', producto=producto, action='editar')
    
    return render_template('inventario_form.html', producto=producto, action='editar')

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para eliminar productos.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    producto = Producto.query.get_or_404(id)
    
    try:
        producto.activo = False
        db.session.commit()
        flash('Producto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'danger')
    
    return redirect(url_for('inventario.listar'))

@inventario_bp.route('/consultar-stock')
@login_required
def consultar_stock():
    productos = Producto.query.filter_by(activo=True).all()
    
    # Obtener parámetros de filtro
    orden = request.args.get('orden', 'nombre')  # nombre, stock_asc, stock_desc
    solo_bajo = request.args.get('solo_bajo') == 'true'
    
    # Aplicar filtro de stock bajo
    if solo_bajo:
        productos = [p for p in productos if p.stock_actual <= p.stock_minimo]
    
    # Aplicar ordenamiento
    if orden == 'stock_asc':
        productos.sort(key=lambda p: p.stock_actual)
    elif orden == 'stock_desc':
        productos.sort(key=lambda p: p.stock_actual, reverse=True)
    else:  # nombre (default)
        productos.sort(key=lambda p: p.nombre)
    
    return render_template('consultar_stock.html', productos=productos, orden=orden, solo_bajo=solo_bajo)

# La ruta de reabastecer fue eliminada y reemplazada por redirección a Gastos
# con contabilidad correcta. Si se necesita mantener por compatibilidad,
# descomentar la siguiente versión que redirige a Gastos:
# @inventario_bp.route('/reabastecer/<int:id>', methods=['GET'])
# @login_required
# @rol_requerido('administrador')
# def reabastecer(id):
#     """Redirige a Gastos para reabastecer con contabilidad correcta"""
#     return redirect(url_for('egresos.crear_egreso', reabastecer_producto=id))

@inventario_bp.route('/api/productos-disponibles')
@login_required
def api_productos_disponibles():
    """API para obtener productos disponibles (para gastos de insumos)"""
    productos = Producto.query.filter_by(activo=True).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'precio_costo': float(p.precio_costo),
        'precio_venta': float(p.precio_venta),
        'stock_actual': p.stock_actual
    } for p in productos])

@inventario_bp.route('/api/productos')
@login_required
def api_productos():
    if current_user.rol != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    productos = Producto.query.filter_by(activo=True).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'stock_actual': p.stock_actual,
        'precio_venta': float(p.precio_venta)
    } for p in productos])

@inventario_bp.route('/api/crear-producto', methods=['POST'])
@login_required
@rol_requerido('administrador')
def api_crear_producto():
    """API para crear un nuevo producto (desde gastos de insumos)"""
    try:
        data = request.get_json()
        
        nombre = data.get('nombre')
        precio_costo = Decimal(str(data.get('precio_costo', 0)))
        precio_venta = Decimal(str(data.get('precio_venta', 0)))
        stock_actual = int(data.get('stock_actual', 0))
        stock_minimo = int(data.get('stock_minimo', 0))
        
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        
        if precio_costo <= 0 or precio_venta <= 0:
            return jsonify({'success': False, 'error': 'Los precios deben ser mayores a cero'}), 400
        
        if stock_actual < 0 or stock_minimo < 0:
            return jsonify({'success': False, 'error': 'El stock no puede ser negativo'}), 400
        
        producto = Producto(
            nombre=nombre,
            descripcion='',
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'producto_id': producto.id,
            'message': 'Producto creado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
