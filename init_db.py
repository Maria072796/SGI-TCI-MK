from app import app, db
from models import Usuario, Producto, Venta, DetalleVenta, Egreso, CierreCaja
import sys

def init_database():
    """Inicializa la base de datos creando todas las tablas y un usuario administrador por defecto."""
    
    with app.app_context():
        try:
            print("Verificando conexión a la base de datos...")
            db.engine.connect()
            print("Conexión exitosa a MySQL.")
            
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente.")
            
            # Verificar si ya existe un usuario administrador
            admin_exists = Usuario.query.filter_by(rol='administrador').first()
            
            if not admin_exists:
                print("Creando usuario administrador por defecto...")
                admin = Usuario(
                    username='admin',
                    rol='administrador',
                    nombre_completo='Administrador del Sistema',
                    activo=True
                )
                admin.set_password('admin123')  # Contraseña por defecto - cambiar después
                db.session.add(admin)
                db.session.commit()
                print("Usuario administrador creado exitosamente.")
                print("Username: admin")
                print("Password: admin123")
                print("IMPORTANTE: Cambie esta contraseña después del primer inicio de sesión.")
            else:
                print("Ya existe un usuario administrador en la base de datos.")
            
            print("Inicialización de base de datos completada exitosamente.")
            
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            print("Por favor verifique que:")
            print("1. MySQL esté instalado y ejecutándose")
            print("2. La base de datos 'sgi_tci_mk' exista")
            print("3. Las credenciales en el archivo .env sean correctas")
            sys.exit(1)

if __name__ == '__main__':
    init_database()
