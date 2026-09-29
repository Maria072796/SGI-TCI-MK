from app import app
from models import db, Venta
from sqlalchemy import text

with app.app_context():
    # Verificar configuración detallada de MySQL
    print("=== CONFIGURACIÓN DETALLADA DE MYSQL ===")
    
    # Zonas horarias
    result = db.session.execute(text("SELECT @@global.time_zone, @@session.time_zone"))
    for row in result:
        print(f"Global time_zone: {row[0]}")
        print(f"Session time_zone: {row[1]}")
    
    # Timestamps actuales
    result = db.session.execute(text("SELECT NOW(), UTC_TIMESTAMP()"))
    for row in result:
        print(f"NOW(): {row[0]}")
        print(f"UTC_TIMESTAMP(): {row[1]}")
    
    # Verificar última venta registrada
    venta = Venta.query.order_by(Venta.id.desc()).first()
    if venta:
        print(f"\n=== ÚLTIMA VENTA REGISTRADA ===")
        print(f"Venta ID: {venta.id}")
        print(f"fecha_hora guardada: {venta.fecha_hora}")
        print(f"Estado: {venta.estado}")
