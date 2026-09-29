from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    # Verificar string de conexión MySQL
    print("=== STRING DE CONEXIÓN MYSQL ===")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Verificar si hay charset o timezone en la conexión
    print("\n=== CONSULTA DE TIMESTAMP ===")
    result = db.session.execute(text("SELECT CONNECTION_ID(), USER(), DATABASE()"))
    for row in result:
        print(f"Connection ID: {row[0]}")
        print(f"User: {row[1]}")
        print(f"Database: {row[2]}")
