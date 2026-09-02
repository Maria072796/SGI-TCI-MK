from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'administrador' or 'vendedor'
    nombre_completo = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    ventas = db.relationship('Venta', backref='usuario', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Producto(db.Model):
    __tablename__ = 'producto'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_costo = db.Column(db.Numeric(10, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    detalles_venta = db.relationship('DetalleVenta', backref='producto', lazy=True)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'

class Venta(db.Model):
    __tablename__ = 'venta'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(20), default='confirmada')  # 'confirmada' or 'anulada'
    total = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.Text)
    
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Venta {self.id} - {self.fecha_hora}>'

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<DetalleVenta {self.id} - Producto {self.producto_id}>'

class Egreso(db.Model):
    __tablename__ = 'egreso'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(db.String(50))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    observaciones = db.Column(db.Text)
    
    usuario = db.relationship('Usuario', backref='egresos')
    
    def __repr__(self):
        return f'<Egreso {self.id} - {self.descripcion}>'

class CierreCaja(db.Model):
    __tablename__ = 'cierre_caja'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    total_ventas = db.Column(db.Numeric(10, 2), nullable=False)
    total_egresos = db.Column(db.Numeric(10, 2), nullable=False)
    total_costos = db.Column(db.Numeric(10, 2), nullable=False)
    utilidad_real = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_hora_cierre = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    observaciones = db.Column(db.Text)
    
    usuario = db.relationship('Usuario', backref='cierres_caja')
    
    def __repr__(self):
        return f'<CierreCaja {self.fecha} - {self.utilidad_real}>'
