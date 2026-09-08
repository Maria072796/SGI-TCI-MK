from flask import Flask, request, session
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os
from models import db, Usuario
from utils.seguridad import password_vencida, password_pronto_vencer

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de base de datos MySQL
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'sgi_tci_mk')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    # URL codificada para manejar caracteres especiales en contraseña
    from urllib.parse import quote_plus
    encoded_password = quote_plus(db_password)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensión de base de datos
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar filtros Jinja personalizados
    from utils.formato import registrar_filtros_jinja
    registrar_filtros_jinja(app)
    
    # Registrar blueprints
    from routes.auth_routes import auth_bp
    from routes.inventario_routes import inventario_bp
    from routes.ventas_routes import ventas_bp
    from routes.egresos_routes import egresos_bp
    from routes.reportes_routes import reportes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(egresos_bp)
    app.register_blueprint(reportes_bp)
    
    # Decorador para verificar roles
    from functools import wraps
    from flask import abort, flash, redirect, url_for
    
    def requiere_rol(rol_requerido):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
                if current_user.rol != rol_requerido:
                    flash('No tienes permiso para acceder a esta página.', 'danger')
                    return redirect(url_for('auth.dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # Hacer el decorador disponible globalmente
    app.requiere_rol = requiere_rol
    
    # Before request para validar contraseña vencida
    @app.before_request
    def verificar_password_vencida():
        # Permitir rutas públicas y de cambio de contraseña
        rutas_permitidas = ['auth.login', 'auth.logout', 'auth.cambiar_password', 'static']
        
        if current_user.is_authenticated:
            endpoint = request.endpoint
            if endpoint and not any(permitida in endpoint for permitida in rutas_permitidas):
                # Verificar si debe cambiar contraseña
                if current_user.debe_cambiar_password:
                    flash('Debes cambiar tu contraseña antes de continuar.', 'warning')
                    return redirect(url_for('auth.cambiar_password'))
                
                # Verificar si la contraseña está vencida
                vencida, dias_restantes = password_vencida(current_user)
                if vencida:
                    flash('Tu contraseña ha vencido. Debes cambiarla para continuar.', 'warning')
                    return redirect(url_for('auth.cambiar_password'))
                
                # Verificar si la contraseña está próxima a vencer (mostrar aviso en dashboard)
                pronto_vencer, dias = password_pronto_vencer(current_user)
                if pronto_vencer and endpoint == 'auth.dashboard':
                    flash(f'Tu contraseña vence en {dias} días. Te recomendamos cambiarla pronto.', 'warning')
    
    return app

app = create_app()

if __name__ == '__main__':
    # Leer puerto desde variable de entorno (Railway) o usar 5000 localmente
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
