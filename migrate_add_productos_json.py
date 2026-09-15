import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

def add_productos_json_column():
    """Agrega la columna productos_json a la tabla egreso."""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME', 'sgi_tci_mk')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    try:
        print(f"Conectando a MySQL en {db_host}:{db_port}...")
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = connection.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("SHOW COLUMNS FROM egreso LIKE 'productos_json'")
        result = cursor.fetchone()
        
        if result:
            print("OK: La columna 'productos_json' ya existe en la tabla egreso.")
        else:
            print("Agregando columna 'productos_json' a la tabla egreso...")
            cursor.execute("ALTER TABLE egreso ADD COLUMN productos_json TEXT")
            connection.commit()
            print("OK: Columna 'productos_json' agregada exitosamente.")
        
        cursor.close()
        connection.close()
        print("OK: Migracion completada exitosamente.")
        return True
        
    except Error as e:
        print(f"ERROR: Error de MySQL: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: Error inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Migracion: Agregar columna productos_json a tabla egreso")
    print("=" * 60)
    print()
    
    if add_productos_json_column():
        sys.exit(0)
    else:
        sys.exit(1)
