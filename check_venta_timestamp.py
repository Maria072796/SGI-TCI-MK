from app import app
from models import db, Venta
from sqlalchemy import text
from datetime import datetime

with app.app_context():
    # Crear una venta de prueba directa para ver qué hora se guarda
    print("=== PRUEBA DE INSERCIÓN DIRECTA ===")
    print(f"datetime.now() en Python: {datetime.now()}")
    
    # Insertar un registro de prueba temporal
    result = db.session.execute(text("INSERT INTO venta (usuario_id, total, estado, fecha_hora) VALUES (1, 100.00, 'confirmada', NOW())"))
    db.session.commit()
    
    # Recuperar el registro insertado
    result = db.session.execute(text("SELECT id, fecha_hora FROM venta WHERE usuario_id = 1 ORDER BY id DESC LIMIT 1"))
    for row in result:
        print(f"Venta de prueba insertada - ID: {row[0]}, fecha_hora: {row[1]}")
    
    # Borrar el registro de prueba
    db.session.execute(text("DELETE FROM venta WHERE usuario_id = 1 AND total = 100.00"))
    db.session.commit()
