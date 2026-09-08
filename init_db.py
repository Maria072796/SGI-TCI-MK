from app import app, db
from models import Usuario, Producto, Venta, DetalleVenta, Egreso, CierreCaja
import sys

def init_database():
    """Inicializa la base de datos creando todas las tablas y usuarios por defecto."""
    
    with app.app_context():
        try:
            print("Verificando conexión a la base de datos...")
            db.engine.connect()
            print("Conexión exitosa a MySQL.")
            
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente.")
            
            # Verificar si ya existe un usuario administrador
            admin_exists = Usuario.query.filter_by(username='admin').first()
            
            if not admin_exists:
                print("Creando usuario administrador por defecto...")
                admin = Usuario(
                    username='admin',
                    rol='administrador',
                    nombre_completo='Administrador del Sistema',
                    activo=True,
                    debe_cambiar_password=True  # [NUEVO] Obligar cambio en primer inicio
                )
                admin.set_password('Admin@2026')  # [NUEVO] Contraseña temporal que cumple política
                db.session.add(admin)
                db.session.commit()
                print("Usuario administrador creado exitosamente.")
                print("Username: admin")
                print("Password: Admin@2026")
                print("IMPORTANTE: Debe cambiar esta contraseña en el primer inicio de sesión.")
            else:
                print("Ya existe un usuario administrador en la base de datos.")
            
            # Verificar si existe usuario vendedor
            vendedor_exists = Usuario.query.filter_by(username='vendedor').first()
            
            if not vendedor_exists:
                print("Creando usuario vendedor por defecto...")
                vendedor = Usuario(
                    username='vendedor',
                    rol='vendedor',
                    nombre_completo='Vendedor del Sistema',
                    activo=True,
                    debe_cambiar_password=True  # [NUEVO] Obligar cambio en primer inicio
                )
                vendedor.set_password('Venta*2026')  # [NUEVO] Contraseña temporal que cumple política
                db.session.add(vendedor)
                db.session.commit()
                print("Usuario vendedor creado exitosamente.")
                print("Username: vendedor")
                print("Password: Venta*2026")
                print("IMPORTANTE: Debe cambiar esta contraseña en el primer inicio de sesión.")
            else:
                print("Ya existe un usuario vendedor en la base de datos.")
            
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
