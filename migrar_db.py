from app import app, db
from models import Usuario, CierreCaja
from sqlalchemy import text

def migrar_base_datos():
    """Aplica migraciones necesarias para la versión 3."""
    
    with app.app_context():
        try:
            print("Verificando conexión a la base de datos...")
            db.engine.connect()
            print("Conexión exitosa a MySQL.")
            
            print("Aplicando migraciones...")
            
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            usuario_columns = [col['name'] for col in inspector.get_columns('usuario')]
            cierre_columns = [col['name'] for col in inspector.get_columns('cierre_caja')]
            
            # Migración de tabla usuario
            if 'fecha_cambio_password' not in usuario_columns:
                print("Agregando columna fecha_cambio_password a usuario...")
                db.session.execute(text('ALTER TABLE usuario ADD COLUMN fecha_cambio_password DATETIME DEFAULT CURRENT_TIMESTAMP AFTER fecha_creacion'))
                db.session.commit()
            
            if 'debe_cambiar_password' not in usuario_columns:
                print("Agregando columna debe_cambiar_password a usuario...")
                db.session.execute(text('ALTER TABLE usuario ADD COLUMN debe_cambiar_password BOOLEAN DEFAULT FALSE AFTER fecha_cambio_password'))
                db.session.commit()
            
            # Migración de tabla cierre_caja
            if 'tipo' not in cierre_columns:
                print("Agregando columna tipo a cierre_caja...")
                db.session.execute(text("ALTER TABLE cierre_caja ADD COLUMN tipo VARCHAR(10) DEFAULT 'dia' AFTER observaciones"))
                db.session.commit()
            
            print("Migraciones aplicadas exitosamente.")
            
            # Actualizar usuarios existentes con valores por defecto
            print("Actualizando usuarios existentes...")
            usuarios = Usuario.query.all()
            for usuario in usuarios:
                if not usuario.fecha_cambio_password:
                    usuario.fecha_cambio_password = usuario.fecha_creacion
                if usuario.debe_cambiar_password is None:
                    usuario.debe_cambiar_password = False
            db.session.commit()
            
            print("Base de datos migrada exitosamente a la versión 3.")
            
        except Exception as e:
            print(f"Error al migrar la base de datos: {e}")
            print("Si las columnas ya existen, este error puede ignorarse.")

if __name__ == '__main__':
    migrar_base_datos()