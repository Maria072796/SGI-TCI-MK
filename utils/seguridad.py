from functools import wraps
from flask import abort, flash, redirect, url_for, session
from flask_login import current_user
from datetime import datetime, timedelta
import re

def validar_password(password):
    """
    Valida una contraseña según la política de seguridad.
    Retorna (valido, mensaje_error)
    """
    errores = []
    
    # Longitud mínima de 8 caracteres
    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres.")
    
    # Al menos un carácter especial: @ + / *
    caracteres_especiales = ['@', '+', '/', '*']
    if not any(char in password for char in caracteres_especiales):
        errores.append("La contraseña debe incluir al menos uno de estos símbolos: @ + / *")
    
    # Al menos una letra y un número
    tiene_letra = any(c.isalpha() for c in password)
    tiene_numero = any(c.isdigit() for c in password)
    if not (tiene_letra and tiene_numero):
        errores.append("La contraseña debe combinar letras y números.")
    
    return (len(errores) == 0, errores)

def password_vencida(usuario):
    """
    Verifica si la contraseña de un usuario está vencida (más de 180 días).
    Retorna (vencida, dias_restantes)
    """
    if not usuario.fecha_cambio_password:
        return (False, 180)
    
    dias_pasados = (datetime.utcnow() - usuario.fecha_cambio_password).days
    vencida = dias_pasados >= 180
    dias_restantes = 180 - dias_pasados
    
    return (vencida, dias_restantes)

def password_pronto_vencer(usuario):
    """
    Verifica si la contraseña vence en menos de 15 días.
    """
    vencida, dias_restantes = password_vencida(usuario)
    return (not vencida and dias_restantes <= 15, dias_restantes)

def rol_requerido(rol_requerido):
    """
    Decorador para verificar que el usuario tenga el rol requerido.
    """
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