from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    # Verificar zona horaria de MySQL
    result = db.session.execute(text("SELECT @@global.time_zone, @@session.time_zone, NOW(), UTC_TIMESTAMP()"))
    print("Zona horaria MySQL:")
    for row in result:
        print(f"  Global time_zone: {row[0]}")
        print(f"  Session time_zone: {row[1]}")
        print(f"  NOW(): {row[2]}")
        print(f"  UTC_TIMESTAMP(): {row[3]}")
