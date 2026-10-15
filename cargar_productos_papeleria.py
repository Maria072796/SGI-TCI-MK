from app import app, db
from models import Producto

productos_papeleria = [
    {
        'nombre': 'Cuaderno A4 100 hojas',
        'descripcion': 'Cuaderno espiral A4 100 hojas rayadas',
        'precio_costo': 3500,
        'precio_venta': 5000,
        'stock_actual': 50,
        'stock_minimo': 10
    },
    {
        'nombre': 'Bolígrafo azul',
        'descripcion': 'Bolígrafo de tinta azul punta fina',
        'precio_costo': 800,
        'precio_venta': 1200,
        'stock_actual': 100,
        'stock_minimo': 20
    },
    {
        'nombre': 'Bolígrafo negro',
        'descripcion': 'Bolígrafo de tinta negra punta fina',
        'precio_costo': 800,
        'precio_venta': 1200,
        'stock_actual': 100,
        'stock_minimo': 20
    },
    {
        'nombre': 'Lápiz HB',
        'descripcion': 'Lápiz grafito HB',
        'precio_costo': 500,
        'precio_venta': 800,
        'stock_actual': 150,
        'stock_minimo': 30
    },
    {
        'nombre': 'Goma de borrar',
        'descripcion': 'Goma de borrar blanca',
        'precio_costo': 400,
        'precio_venta': 700,
        'stock_actual': 80,
        'stock_minimo': 15
    },
    {
        'nombre': 'Regla 30cm',
        'descripcion': 'Regla plástica 30cm transparente',
        'precio_costo': 1200,
        'precio_venta': 1800,
        'stock_actual': 40,
        'stock_minimo': 10
    },
    {
        'nombre': 'Resaltador amarillo',
        'descripcion': 'Marcador resaltador amarillo',
        'precio_costo': 1500,
        'precio_venta': 2200,
        'stock_actual': 60,
        'stock_minimo': 15
    },
    {
        'nombre': 'Resaltador verde',
        'descripcion': 'Marcador resaltador verde',
        'precio_costo': 1500,
        'precio_venta': 2200,
        'stock_actual': 60,
        'stock_minimo': 15
    },
    {
        'nombre': 'Resaltador rosa',
        'descripcion': 'Marcador resaltador rosa',
        'precio_costo': 1500,
        'precio_venta': 2200,
        'stock_actual': 60,
        'stock_minimo': 15
    },
    {
        'nombre': 'Corrector líquido',
        'descripcion': 'Corrector líquido 8ml',
        'precio_costo': 2000,
        'precio_venta': 3000,
        'stock_actual': 35,
        'stock_minimo': 10
    },
    {
        'nombre': 'Pegamento en barra',
        'descripcion': 'Pegamento en barra 20g',
        'precio_costo': 1200,
        'precio_venta': 1800,
        'stock_actual': 45,
        'stock_minimo': 10
    },
    {
        'nombre': 'Tijeras escolares',
        'descripcion': 'Tijeras escolares 13cm',
        'precio_costo': 3500,
        'precio_venta': 5000,
        'stock_actual': 25,
        'stock_minimo': 8
    },
    {
        'nombre': 'Carpeta cartón A4',
        'descripcion': 'Carpeta de cartón A4 amarilla',
        'precio_costo': 800,
        'precio_venta': 1200,
        'stock_actual': 100,
        'stock_minimo': 20
    },
    {
        'nombre': 'Sobre manila A4',
        'descripcion': 'Sobre manila A4',
        'precio_costo': 300,
        'precio_venta': 500,
        'stock_actual': 200,
        'stock_minimo': 50
    },
    {
        'nombre': 'Papel bond carta 500 hojas',
        'descripcion': 'Resma papel bond carta 500 hojas',
        'precio_costo': 15000,
        'precio_venta': 20000,
        'stock_actual': 20,
        'stock_minimo': 5
    },
    {
        'nombre': 'Papel bond oficio 500 hojas',
        'descripcion': 'Resma papel bond oficio 500 hojas',
        'precio_costo': 13000,
        'precio_venta': 17500,
        'stock_actual': 20,
        'stock_minimo': 5
    },
    {
        'nombre': 'Calculadora básica',
        'descripcion': 'Calculadora básica de escritorio',
        'precio_costo': 12000,
        'precio_venta': 18000,
        'stock_actual': 15,
        'stock_minimo': 5
    },
    {
        'nombre': 'Marcador pizarra negro',
        'descripcion': 'Marcador pizarra negro borrable',
        'precio_costo': 2000,
        'precio_venta': 3000,
        'stock_actual': 40,
        'stock_minimo': 10
    },
    {
        'nombre': 'Marcador pizarra azul',
        'descripcion': 'Marcador pizarra azul borrable',
        'precio_costo': 2000,
        'precio_venta': 3000,
        'stock_actual': 40,
        'stock_minimo': 10
    },
    {
        'nombre': 'Marcador pizarra rojo',
        'descripcion': 'Marcador pizarra rojo borrable',
        'precio_costo': 2000,
        'precio_venta': 3000,
        'stock_actual': 40,
        'stock_minimo': 10
    },
    {
        'nombre': 'Borrador pizarra',
        'descripcion': 'Borrador de pizarra',
        'precio_costo': 3000,
        'precio_venta': 4500,
        'stock_actual': 20,
        'stock_minimo': 5
    }
]

def cargar_productos():
    """Carga productos de papelería en la base de datos."""
    with app.app_context():
        print("=== Cargando productos de papelería ===")
        
        productos_agregados = 0
        productos_actualizados = 0
        
        for prod_data in productos_papeleria:
            # Verificar si el producto ya existe
            producto_existente = Producto.query.filter_by(nombre=prod_data['nombre']).first()
            
            if producto_existente:
                # Actualizar producto existente
                producto_existente.descripcion = prod_data['descripcion']
                producto_existente.precio_costo = prod_data['precio_costo']
                producto_existente.precio_venta = prod_data['precio_venta']
                producto_existente.stock_actual = prod_data['stock_actual']
                producto_existente.stock_minimo = prod_data['stock_minimo']
                producto_existente.activo = True
                productos_actualizados += 1
                print(f"[OK] Actualizado: {prod_data['nombre']}")
            else:
                # Crear nuevo producto
                nuevo_producto = Producto(
                    nombre=prod_data['nombre'],
                    descripcion=prod_data['descripcion'],
                    precio_costo=prod_data['precio_costo'],
                    precio_venta=prod_data['precio_venta'],
                    stock_actual=prod_data['stock_actual'],
                    stock_minimo=prod_data['stock_minimo'],
                    activo=True
                )
                db.session.add(nuevo_producto)
                productos_agregados += 1
                print(f"[OK] Agregado: {prod_data['nombre']}")

        db.session.commit()

        print(f"\n=== Resumen ===")
        print(f"Productos agregados: {productos_agregados}")
        print(f"Productos actualizados: {productos_actualizados}")
        print(f"Total procesados: {productos_agregados + productos_actualizados}")
        print("\n[OK] Carga completada exitosamente.")

if __name__ == '__main__':
    cargar_productos()
