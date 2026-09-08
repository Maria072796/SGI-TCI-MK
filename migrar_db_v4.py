from app import app, db
from models import Usuario, Venta, DetalleVenta, Egreso, CierreCaja
from sqlalchemy import text

def migrar_base_datos_v4():
    """Aplica migraciones necesarias para la versión 4."""
    
    with app.app_context():
        try:
            print("Verificando conexión a la base de datos...")
            db.engine.connect()
            print("Conexión exitosa a MySQL.")
            
            print("Aplicando migraciones versión 4...")
            
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            venta_columns = [col['name'] for col in inspector.get_columns('venta')]
            detalle_columns = [col['name'] for col in inspector.get_columns('detalle_venta')]
            egreso_columns = [col['name'] for col in inspector.get_columns('egreso')]
            cierre_columns = [col['name'] for col in inspector.get_columns('cierre_caja')]
            
            # Migración de tabla venta
            if 'fecha_anulacion' not in venta_columns:
                print("Agregando columna fecha_anulacion a venta...")
                db.session.execute(text('ALTER TABLE venta ADD COLUMN fecha_anulacion DATETIME'))
                db.session.commit()
            
            if 'anulada_por' not in venta_columns:
                print("Agregando columna anulada_por a venta...")
                db.session.execute(text('ALTER TABLE venta ADD COLUMN anulada_por INT'))
                db.session.commit()
            
            if 'motivo_anulacion' not in venta_columns:
                print("Agregando columna motivo_anulacion a venta...")
                db.session.execute(text('ALTER TABLE venta ADD COLUMN motivo_anulacion TEXT'))
                db.session.commit()
            
            # Migración de tabla detalle_venta
            if 'costo_unitario' not in detalle_columns:
                print("Agregando columna costo_unitario a detalle_venta...")
                db.session.execute(text('ALTER TABLE detalle_venta ADD COLUMN costo_unitario DECIMAL(10,2)'))
                db.session.commit()
            
            # Migración de tabla egreso
            if 'activo' not in egreso_columns:
                print("Agregando columna activo a egreso...")
                db.session.execute(text('ALTER TABLE egreso ADD COLUMN activo BOOLEAN DEFAULT TRUE'))
                db.session.commit()
            
            # Migración de tabla cierre_caja
            if 'cantidad_ventas' not in cierre_columns:
                print("Agregando columna cantidad_ventas a cierre_caja...")
                db.session.execute(text('ALTER TABLE cierre_caja ADD COLUMN cantidad_ventas INT DEFAULT 0'))
                db.session.commit()
            
            print("Migraciones versión 4 aplicadas exitosamente.")
            
            # Actualizar datos existentes con valores por defecto
            print("Actualizando datos existentes...")
            
            # Actualizar egresos existentes
            egresos = Egreso.query.all()
            for egreso in egresos:
                if egreso.activo is None:
                    egreso.activo = True
            db.session.commit()
            
            # Actualizar cierres existentes
            cierres = CierreCaja.query.all()
            for cierre in cierres:
                if cierre.cantidad_ventas is None:
                    cierre.cantidad_ventas = 0
            db.session.commit()
            
            print("Base de datos migrada exitosamente a la versión 4.")
            
        except Exception as e:
            print(f"Error al migrar la base de datos: {e}")
            print("Si las columnas ya existen, este error puede ignorarse.")

if __name__ == '__main__':
    migrar_base_datos_v4()