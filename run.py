import os
import sys
from dotenv import load_dotenv

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()



def verificar_variables_entorno():
    """Verifica que las variables de entorno necesarias estén configuradas."""
    variables_requeridas = ['SECRET_KEY']
    variables_faltantes = []
    
    for var in variables_requeridas:
        if not os.getenv(var):
            variables_faltantes.append(var)
    
    if variables_faltantes:
        print("✗ Faltan las siguientes variables de entorno:")
        for var in variables_faltantes:
            print(f"  - {var}")
        print("\nPor favor configure estas variables en el archivo .env")
        print("Puede copiar .env.example a .env y configurar los valores.")
        return False
    
    print("✓ Variables de entorno configuradas correctamente.")
    return True

def inicializar_base_datos():
    """Ejecuta init_db.py si las tablas no existen."""
    try:
        print("Verificando si es necesario inicializar la base de datos...")
        
        # Importar después de verificar variables de entorno
        from app import app, db
        from models import Usuario
        from sqlalchemy import inspect
        
        with app.app_context():
            # Verificar si la tabla usuario existe
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            if 'usuario' not in tablas_existentes:
                print("Tablas no encontradas. Inicializando base de datos...")
                import init_db
                init_db.init_database()
            else:
                print("✓ Base de datos ya inicializada.")
                
                # Verificar si existe usuario administrador
                admin_exists = Usuario.query.filter_by(rol='administrador').first()
                if not admin_exists:
                    print("Creando usuario administrador por defecto...")
                    admin = Usuario(
                        username='admin',
                        rol='administrador',
                        nombre_completo='Administrador del Sistema',
                        activo=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    print("✓ Usuario administrador creado:")
                    print("  Username: admin")
                    print("  Password: admin123")
                    print("  IMPORTANTE: Cambie esta contraseña después del primer inicio de sesión.")
                else:
                    print("✓ Usuario administrador existe.")
                    
    except Exception as e:
        print(f"✗ Error al inicializar la base de datos: {str(e)}")
        return False
    
    return True

def main():
    """Función principal para iniciar la aplicación."""
    print("=" * 60)
    print("SGI-TCI MK - Sistema de Gestión de Inventario")
    print("Miscelánea Karen@")
    print("=" * 60)
    print()
    
    # Verificar variables de entorno
    if not verificar_variables_entorno():
        sys.exit(1)
    
    print()
    
    # Inicializar base de datos si es necesario
    if not inicializar_base_datos():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Iniciando aplicación Flask...")
    print("=" * 60)
    print()
    
    # Importar y ejecutar la aplicación
    from app import app
    
    # Ejecutar en modo desarrollo solo en local
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Modo debug: {debug_mode}")
    print(f"La aplicación estará disponible en: http://localhost:5000")
    print()
    print("Presione Ctrl+C para detener la aplicación.")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=debug_mode)
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario.")
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
