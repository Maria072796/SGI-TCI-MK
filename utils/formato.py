from flask import Blueprint
from datetime import datetime, timedelta, timezone

def ahora_colombia():
    """
    Retorna la fecha y hora actual en zona horaria de Colombia (UTC-5).
    Devuelve un datetime naive (sin tzinfo) para compatibilidad con MySQL.
    Funciona correctamente sin importar la zona horaria del servidor.
    """
    # Obtener hora UTC actual
    ahora_utc = datetime.now(timezone.utc)
    # Restar 5 horas para obtener hora de Colombia (UTC-5)
    ahora_colombia = ahora_utc + timedelta(hours=-5)
    # Convertir a naive (quitar tzinfo)
    return ahora_colombia.replace(tzinfo=None)

def hoy_colombia():
    """
    Retorna la fecha actual en zona horaria de Colombia (UTC-5).
    """
    return ahora_colombia().date()

def formatear_moneda(valor):
    """Formatea un valor numérico como moneda colombiana sin decimales."""
    try:
        valor_float = float(valor)
        # Redondear al entero más cercano
        valor_redondeado = round(valor_float)
        # Formatear con punto como separador de miles
        return f"${valor_redondeado:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return valor

def formatear_fecha(fecha):
    """Formatea una fecha en formato corto DD/MM/YYYY."""
    if fecha:
        return fecha.strftime('%d/%m/%Y')
    return fecha

def formatear_fecha_hora(fecha_hora):
    """Formatea una fecha y hora en formato DD/MM/YYYY HH:MM."""
    if fecha_hora:
        return fecha_hora.strftime('%d/%m/%Y %H:%M')
    return fecha_hora

def registrar_filtros_jinja(app):
    """Registra filtros personalizados en Jinja2."""
    @app.template_filter('moneda')
    def filtro_moneda(valor):
        return formatear_moneda(valor)
    
    @app.template_filter('fecha_corta')
    def filtro_fecha_corta(valor):
        return formatear_fecha(valor)
    
    @app.template_filter('fecha_hora')
    def filtro_fecha_hora(valor):
        return formatear_fecha_hora(valor)