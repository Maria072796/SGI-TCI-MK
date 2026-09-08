from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Producto
from decimal import Decimal

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
@login_required
def listar():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para acceder al inventario.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('inventario.html', productos=productos)

@inventario_bp.route('/crear', methods=['GET', 'POST'])
@login_required
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
