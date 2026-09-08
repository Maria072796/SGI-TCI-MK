# Prompt de Implementación — SGI-TCI MK (Miscelánea Karen@) - VERSIÓN ACTUALIZADA

## Descripción General
Debes implementar una aplicación web completa para gestionar el inventario, las ventas y la trazabilidad de costos e ingresos de la Miscelánea Karen@, usando Flask con MySQL, con las siguientes especificaciones actualizadas:

## Requisitos Funcionales

### Gestión de Inventario
El sistema debe gestionar un catálogo de productos, permitiendo:
- Registrar productos con sus características físicas y económicas
- Actualizar información de productos existentes
- Consultar el inventario disponible
- Control básico de los productos registrados dentro del sistema (eliminación lógica)

### Gestión de Ventas
El sistema debe permitir registrar ventas:
- Seleccionando uno o varios productos del inventario
- Calculando el total automáticamente en tiempo real
- Descontando stock automáticamente al confirmar
- Anulando ventas ya registradas (revirtiendo el stock descontado)
- Generando información necesaria para el cierre de caja

### Gestión de Egresos
El sistema debe permitir:
- Registrar egresos del negocio
- Consultar egresos registrados
- Editar y eliminar egresos

### Reportes Financieros
El sistema debe calcular y mostrar:
- Utilidad real diaria (ingresos por ventas − costos de productos vendidos − egresos)
- Cierre de caja diario con: total de ventas, total de egresos, total de costos y utilidad real
- Reportes financieros por período personalizable
- Historial de cierres de caja

### Gestión de Usuarios
El sistema debe incluir gestión completa de usuarios:
- Crear nuevos usuarios con roles (administrador/vendedor)
- Editar usuarios existentes
- Eliminar usuarios (soft delete)
- Listar todos los usuarios del sistema
- Protección contra eliminación del último administrador

## Datos de las Entidades

### Producto
- id, nombre, descripción, precio de costo, precio de venta, stock actual, stock mínimo, estado (activo/inactivo)

### Venta
- id, fecha/hora, usuario que la realizó, estado (confirmada/anulada), total, observaciones
- Detalle: productos, cantidades, subtotales, precio unitario

### Egreso
- id, descripción, monto, categoría, fecha/hora, usuario, observaciones

### Usuario
- id, username, password_hash, rol (administrador/vendedor), nombre_completo, activo, fecha_creación

### CierreCaja
- id, fecha, usuario_id, total_ventas, total_egresos, total_costos, utilidad_real, fecha_hora_cierre, observaciones

## Roles y Autenticación

### Administrador
- Acceso a inventario (CRUD completo)
- Acceso a egresos (CRUD completo)
- Acceso a reportes financieros
- Acceso a cierre de caja
- Acceso a gestión de usuarios
- Dashboard con estadísticas completas

### Vendedor
- Acceso únicamente al módulo de ventas (crear, consultar, anular propias)
- Acceso al cierre de caja de su turno
- Dashboard con estadísticas limitadas
- Sin acceso a inventario, egresos, reportes financieros o gestión de usuarios

### Autenticación
- Autenticación por sesión (Flask-Login)
- Contraseñas hasheadas (werkzeug.security)
- Los usuarios se crean desde la tabla usuario, no se hardcodean en el código
- Gestión de contraseñas segura

## Especificaciones Técnicas

### Entorno de Desarrollo
- Desarrollo en Windows 11
- Backend e interfaz web en Flask (Jinja2 + Bootstrap para las plantillas)
- Base de datos MySQL 8.0 (NO PostgreSQL)
- Acceso a base de datos con Flask-SQLAlchemy usando mysql-connector-python

### Configuración
- Variables de conexión a la base de datos manejadas por variables de entorno (.env con python-dotenv)
- Nunca hardcodeadas
- Codificación URL para contraseñas con caracteres especiales
- Configuración de codificación UTF-8 para Windows

### API
- Sin API pública externa (fuera del alcance del proyecto de grado)
- Si más adelante se requiere, se puede exponer con Flask-RESTful sobre la misma app

## Estructura del Proyecto

Generar el proyecto en: `C:\Users\Maria\OneDrive\Desktop\Universidad\TRABAJO DE GRADO 2\SGI-TCI-MK`

```
SGI-TCI-MK/
├── app.py                    # Punto de entrada, crea y configura la app Flask
├── models.py                 # Modelos SQLAlchemy: Usuario, Producto, Venta, DetalleVenta, Egreso, CierreCaja
├── init_db.py                # Crea las tablas y un usuario administrador inicial
├── run.py                    # Script de inicio con verificaciones y manejo de encoding
├── crear_vendedor.py         # Script auxiliar para crear usuario vendedor de ejemplo
├── routes/
│   ├── __init__.py           # Inicialización del paquete routes
│   ├── auth_routes.py        # Login / logout / dashboard / gestión de usuarios
│   ├── inventario_routes.py  # CRUD de productos
│   ├── ventas_routes.py      # Gestión de ventas con validación de stock
│   ├── egresos_routes.py     # Gestión de egresos
│   └── reportes_routes.py    # Reportes financieros
├── templates/                # Plantillas HTML con Bootstrap
│   ├── base.html            # Plantilla base con navegación por roles
│   ├── login.html           # Página de login
│   ├── dashboard.html       # Dashboard con estadísticas por rol
│   ├── usuarios.html        # Lista y gestión de usuarios
│   ├── usuario_form.html    # Formulario para crear/editar usuarios
│   ├── inventario.html      # Lista de productos
│   ├── inventario_form.html # Formulario de productos
│   ├── ventas.html          # Lista de ventas
│   ├── venta_form.html      # Formulario dinámico de ventas con JavaScript
│   ├── venta_detalle.html   # Detalle de venta específica
│   ├── egresos.html         # Lista de egresos
│   ├── egreso_form.html     # Formulario de egresos
│   ├── utilidad_diaria.html  # Reporte de utilidad diaria
│   ├── cierre_caja.html     # Formulario de cierre de caja
│   ├── historial_cierres.html # Historial de cierres
│   └── reporte_financiero.html # Reporte financiero por período
├── static/                   # Archivos estáticos
│   ├── css/
│   │   └── style.css        # Estilos personalizados
│   └── js/
│       └── main.js          # Funcionalidades JavaScript
├── instance/                 # No se usa para MySQL, pero se mantiene por convención Flask
├── db/
│   └── sgi_tci_mk_der.sql   # Script DDL de referencia
├── .env.example             # Plantilla de variables de entorno
├── .env                     # Variables de entorno configuradas
├── requirements.txt          # Dependencias de Python
├── README.md                # Documentación completa del proyecto
├── CUESTIONARIO_SGI_TCI_MK.md # Cuestionario en Markdown
└── CUESTIONARIO_SGI_TCI_MK.ipynb # Cuestionario en Jupyter Notebook
```

## Requerimientos Específicos

### Base de Datos
- Validar que la relación detalle_venta → venta y detalle_venta → producto funcione correctamente en SQLAlchemy (db.relationship con backref)
- Validar stock disponible antes de confirmar una venta; si no alcanza, mostrar error y no descontar
- Al anular una venta, revertir el stock de cada producto de su detalle
- Manejar correctamente la conexión a MySQL (verificar que la base de datos exista antes de intentar crear las tablas; capturar errores de conexión con mensaje claro)
- Soporte para caracteres especiales en contraseñas mediante codificación URL

### Funcionalidades del Sistema
- Actualizar la caja/utilidad automáticamente al generar un cierre, no manualmente
- Implementar JavaScript funcional para: agregar productos dinámicamente a una venta, calcular subtotales y total en tiempo real antes de enviar el formulario
- Restringir cada ruta según el rol del usuario autenticado (verificación en cada ruta)
- Dashboard adaptado según rol del usuario (estadísticas diferentes para admin y vendedor)

### Gestión de Usuarios
- Implementar CRUD completo de usuarios
- Proteger rutas de gestión de usuarios (solo administrador)
- Validar que no se pueda eliminar el último administrador
- Permitir cambio de contraseña y estado de usuario
- Mostrar estadísticas de usuarios en el dashboard del administrador

### Interfaz de Usuario
- Menú de navegación adaptado según rol del usuario
- Opción "Usuarios" solo visible para administradores
- Mensajes de feedback claros para todas las operaciones
- Validación visual de formularios en frontend y backend
- Diseño responsivo con Bootstrap 5

## requirements.txt
```
flask==3.0.3
flask-sqlalchemy==3.1.1
flask-login==0.6.3
mysql-connector-python==8.0.33
python-dotenv==1.0.1
jinja2==3.1.4
werkzeug==3.0.3
```

## Instrucciones de Ejecución (run.py)

El script run.py debe:

1. Cargar variables de entorno desde .env
2. Configurar codificación UTF-8 para Windows
3. Verificar la conexión a MySQL antes de iniciar (con mensaje de error claro si falla)
4. Ejecutar init_db.py si las tablas no existen (crear tablas + un usuario administrador por defecto)
5. Verificar y crear usuario vendedor si no existe
6. Iniciar la aplicación Flask en modo desarrollo (debug=True solo en local)

## Variables de Entorno (.env)
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sgi_tci_mk
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
SECRET_KEY=tu_clave_secreta
FLASK_DEBUG=True
```

## Credenciales por Defecto

### Administrador
- Username: admin
- Password: admin123
- Rol: administrador

### Vendedor
- Username: vendedor
- Password: vendedor123
- Rol: vendedor

## Validaciones Adicionales

### Backend
- Validación de campos obligatorios en todos los formularios
- Validación de valores numéricos positivos
- Validación que precio de venta > precio de costo
- Validación de stock disponible
- Validación de roles de usuario
- Manejo robusto de errores con rollback de transacciones

### Frontend
- Validación de formularios en JavaScript
- Cálculos automáticos en tiempo real
- Alertas visuales para validaciones
- Feedback inmediato al usuario

## Documentación Adicional

El proyecto debe incluir:
- README.md con instrucciones completas de instalación y uso
- Cuestionario técnico en Markdown (.md)
- Cuestionario interactivo en Jupyter Notebook (.ipynb)
- Comentarios en código para mantenimiento

## Funcionalidades Específicas por Módulo

### Módulo de Inventario (Administrador)
- Registro de nuevos productos con características físicas y económicas
- Actualización de información de productos
- Consulta del inventario disponible
- Control básico de productos registrados

### Módulo de Visualización Financiera (Administrador)
- Consulta de ingresos generados por ventas
- Registro y consulta de egresos
- Visualización de costos asociados al inventario
- Cálculo de utilidad real diaria
- Consulta de información financiera básica del negocio

### Módulo de Ventas (Vendedor)
- Registro de ventas realizadas durante el día
- Selección de uno o varios productos por cada venta
- Confirmación de la venta realizada
- Anulación de ventas en caso de errores en el registro
- Generación de información necesaria para el cierre de caja

## Generar el proyecto completo con:

- Manejo de errores robusto
- Validaciones de formularios en el backend (no solo en JavaScript)
- Interfaz Bootstrap coherente con los dos roles del sistema (Administrador y Vendedor)
- Gestión completa de usuarios
- Codificación UTF-8 para soporte en Windows
- Documentación completa
- Estructura modular y escalable
