from models import db, Venta, DetalleVenta, Egreso, Producto, CierreCaja
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

def calcular_totales(fecha, usuario_id=None):
    """
    Calcula los totales de ventas, costos y egresos para una fecha específica.
    Si usuario_id se proporciona, calcula solo para ese usuario (cierre de turno).
    Si no, calcula para todos los usuarios (cierre del día).
    
    Retorna dict con: {
        'cantidad_ventas': int,
        'total_ventas': Decimal,
        'total_costos': Decimal,
        'total_egresos': Decimal,
        'utilidad_real': Decimal
    }
    """
    # Calcular ventas confirmadas
    ventas_query = Venta.query.filter(
        Venta.estado == 'confirmada',
        func.date(Venta.fecha_hora) == fecha
    )
    
    if usuario_id:
        ventas_query = ventas_query.filter(Venta.usuario_id == usuario_id)
    
    ventas = ventas_query.all()
    cantidad_ventas = len(ventas)
    total_ventas = sum(v.total for v in ventas)
    
    # Calcular costos de productos vendidos
    total_costos = Decimal('0')
    for venta in ventas:
        for detalle in venta.detalles:
            total_costos += detalle.costo_unitario * detalle.cantidad
    
    # Calcular egresos (solo para cierre del día, no para turno)
    total_egresos = Decimal('0')
    if not usuario_id:
        egresos = Egreso.query.filter(
            Egreso.activo == True,
            func.date(Egreso.fecha_hora) == fecha
        ).all()
        total_egresos = sum(e.monto for e in egresos)
    
    # Calcular utilidad real (RN-10)
    utilidad_real = total_ventas - total_costos - total_egresos
    
    return {
        'cantidad_ventas': cantidad_ventas,
        'total_ventas': total_ventas,
        'total_costos': total_costos,
        'total_egresos': total_egresos,
        'utilidad_real': utilidad_real
    }

def calcular_utilidad(ventas_totales, costos_totales, egresos_totales):
    """
    Calcula la utilidad real según RN-10: ventas - costos - egresos.
    """
    return ventas_totales - costos_totales - egresos_totales

def productos_mas_vendidos(fecha_inicio=None, fecha_fin=None, limite=5):
    """
    Retorna los productos más vendidos en un período.
    """
    query = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_cantidad'),
        func.sum(DetalleVenta.subtotal).label('total_ventas')
    ).join(
        DetalleVenta, Producto.id == DetalleVenta.producto_id
    ).join(
        Venta, DetalleVenta.venta_id == Venta.id
    ).filter(
        Venta.estado == 'confirmada'
    )
    
    if fecha_inicio and fecha_fin:
        query = query.filter(
            func.date(Venta.fecha_hora) >= fecha_inicio,
            func.date(Venta.fecha_hora) <= fecha_fin
        )
    
    query = query.group_by(Producto.id, Producto.nombre).order_by(
        func.sum(DetalleVenta.cantidad).desc()
    ).limit(limite)
    
    return query.all()

def valor_inventario_total():
    """
    Calcula el valor total del inventario actual (stock * precio_costo).
    """
    productos = Producto.query.filter_by(activo=True).all()
    valor_total = sum(p.stock_actual * p.precio_costo for p in productos)
    return valor_total

def productos_bajo_stock():
    """
    Retorna productos con stock actual <= stock mínimo.
    """
    return Producto.query.filter(
        Producto.activo == True,
        Producto.stock_actual <= Producto.stock_minimo
    ).all()

def usuario_cerro_caja_hoy(usuario_id, fecha=None):
    """
    Verifica si un usuario ya cerró caja hoy.
    Si fecha no se proporciona, usa la fecha actual.
    Retorna True si ya cerró caja, False en caso contrario.
    """
    if fecha is None:
        fecha = date.today()
    
    cierre = CierreCaja.query.filter_by(
        fecha=fecha,
        usuario_id=usuario_id
    ).first()
    
    return cierre is not None

def egresos_del_periodo(fecha_inicio, fecha_fin):
    """
    Retorna los egresos activos del período especificado.
    Excluye egresos de categoría "Compra de insumos" (ya se reflejan como costo en ventas).
    """
    egresos = Egreso.query.filter(
        Egreso.activo == True,
        Egreso.categoria != 'Compra de insumos',
        func.date(Egreso.fecha_hora) >= fecha_inicio,
        func.date(Egreso.fecha_hora) <= fecha_fin
    ).all()
    
    return egresos