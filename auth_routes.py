from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from datetime import datetime
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor ingrese usuario y contraseña.', 'warning')
            return render_template('login.html')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.activo:
                flash('Su cuenta está desactivada. Contacte al administrador.', 'danger')
                return render_template('login.html')
            
            login_user(user)
            flash(f'Bienvenido, {user.nombre_completo or user.username}!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    from models import Producto, Venta
    from sqlalchemy import func
    
    # Estadísticas básicas
    total_productos = Producto.query.filter_by(activo=True).count()
    productos_bajo_stock = Producto.query.filter(
        Producto.activo == True,
        Producto.stock_actual <= Producto.stock_minimo
    ).count()
    
    ventas_hoy = Venta.query.filter(
        Venta.estado == 'confirmada',
        func.date(Venta.fecha_hora) == datetime.utcnow().date()
    ).count()
    
    # Total de usuarios por rol
    total_admins = Usuario.query.filter_by(rol='administrador', activo=True).count()
    total_vendedores = Usuario.query.filter_by(rol='vendedor', activo=True).count()
    
    return render_template('dashboard.html', 
                          total_productos=total_productos,
                          productos_bajo_stock=productos_bajo_stock,
                          ventas_hoy=ventas_hoy,
                          total_admins=total_admins,
                          total_vendedores=total_vendedores)

# Gestión de usuarios (solo administrador)
@auth_bp.route('/usuarios')
@login_required
def listar_usuarios():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para gestionar usuarios.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para crear usuarios.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            nombre_completo = request.form.get('nombre_completo')
            rol = request.form.get('rol')
            
            if not username or not password or not rol:
                flash('Por favor complete todos los campos obligatorios.', 'warning')
                return render_template('usuario_form.html', action='crear')
            
            # Verificar que el username no exista
            if Usuario.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe.', 'danger')
                return render_template('usuario_form.html', action='crear')
            
            usuario = Usuario(
                username=username,
                nombre_completo=nombre_completo,
                rol=rol,
                activo=True
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('auth.listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {str(e)}', 'danger')
            return render_template('usuario_form.html', action='crear')
    
    return render_template('usuario_form.html', action='crear')

@auth_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para editar usuarios.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nombre_completo = request.form.get('nombre_completo')
            usuario.rol = request.form.get('rol')
            usuario.activo = 'activo' in request.form
            
            password = request.form.get('password')
            if password:
                usuario.set_password(password)
            
            db.session.commit()
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('auth.listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
            return render_template('usuario_form.html', usuario=usuario, action='editar')
    
    return render_template('usuario_form.html', usuario=usuario, action='editar')

@auth_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    if current_user.rol != 'administrador':
        flash('No tienes permiso para eliminar usuarios.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    
    # No permitir eliminar el último administrador
    if usuario.rol == 'administrador':
        admin_count = Usuario.query.filter_by(rol='administrador', activo=True).count()
        if admin_count <= 1:
            flash('No se puede eliminar el último administrador.', 'danger')
            return redirect(url_for('auth.listar_usuarios'))
    
    try:
        usuario.activo = False
        db.session.commit()
        flash('Usuario eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    
    return redirect(url_for('auth.listar_usuarios'))
