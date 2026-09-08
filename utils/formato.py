from flask import Blueprint

def formatear_moneda(valor):
    """Formatea un valor numérico como moneda colombiana."""
    try:
        valor_float = float(valor)
        return f"${valor_float:,.2f}"
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