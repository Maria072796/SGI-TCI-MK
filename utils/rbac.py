from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def requiere_rol(*roles_requeridos):
    """
    Decorador para verificar que el usuario tenga uno de los roles requeridos.
    Puede aceptar un solo rol o múltiples roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.rol not in roles_requeridos:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return redirect(url_for('auth.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def solo_admin(f):
    """Decorador shortcut para verificar que el usuario sea administrador."""
    return requiere_rol('administrador')(f)

def requiere_admin_o_vendedor(f):
    """Decorador para verificar que el usuario sea administrador o vendedor."""
    return requiere_rol('administrador', 'vendedor')(f)
