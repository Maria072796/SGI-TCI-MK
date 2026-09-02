from app import app, db
from models import Usuario
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

with app.app_context():
    # Verificar si ya existe un vendedor
    vendedor_exists = Usuario.query.filter_by(username='vendedor').first()
    
    if not vendedor_exists:
        print("Creando usuario vendedor de ejemplo...")
        vendedor = Usuario(
            username='vendedor',
            rol='vendedor',
            nombre_completo='Vendedor de Ejemplo',
            activo=True
        )
        vendedor.set_password('vendedor123')
        db.session.add(vendedor)
        db.session.commit()
        print("Usuario vendedor creado exitosamente:")
        print("  Username: vendedor")
        print("  Password: vendedor123")
        print("  Rol: vendedor")
    else:
        print("El usuario vendedor ya existe.")
    
    # Mostrar todos los usuarios
    print("\nUsuarios en el sistema:")
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        estado = "Activo" if usuario.activo else "Inactivo"
        print(f"  - {usuario.username} ({usuario.rol}): {estado}")
