from app import app, db
from models import Usuario

def actualizar_usuarios():
    """Actualiza las contraseñas de los usuarios existentes a la nueva política."""
    
    with app.app_context():
        try:
            print("Actualizando usuarios existentes...")
            
            # Actualizar admin
            admin = Usuario.query.filter_by(username='admin').first()
            if admin:
                admin.set_password('Admin@2026')
                admin.debe_cambiar_password = True
                print('Admin actualizado: password=Admin@2026, debe_cambiar_password=True')
            
            # Actualizar vendedor
            vendedor = Usuario.query.filter_by(username='vendedor').first()
            if vendedor:
                vendedor.set_password('Venta*2026')
                vendedor.debe_cambiar_password = True
                print('Vendedor actualizado: password=Venta*2026, debe_cambiar_password=True')
            
            db.session.commit()
            print("Usuarios actualizados exitosamente.")
            
        except Exception as e:
            print(f"Error al actualizar usuarios: {e}")
            db.session.rollback()

if __name__ == '__main__':
    actualizar_usuarios()