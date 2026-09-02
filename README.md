# SGI-TCI MK - Sistema de Gestión de Inventario y Trazabilidad de Costos e Ingresos

Sistema web para la gestión de inventario, ventas y trazabilidad financiera de la Miscelánea Karen@.

## Características

- **Gestión de Inventario**: Registro, actualización, consulta y eliminación de productos
- **Gestión de Ventas**: Registro de ventas con cálculo automático de totales y descuento de stock
- **Anulación de Ventas**: Reversión de stock al anular ventas
- **Gestión de Egresos**: Registro y consulta de egresos del negocio
- **Reportes Financieros**: 
  - Utilidad diaria (ingresos - costos - egresos)
  - Cierre de caja diario
  - Reportes financieros por período
- **Control de Acceso**: 
  - Rol Administrador: acceso completo
  - Rol Vendedor: acceso a ventas y cierre de caja
- **Autenticación**: Sesiones con contraseñas hasheadas

## Requisitos

- Python 3.8+
- MySQL 8.0+
- Windows 11

## Instalación

1. **Clonar o copiar el proyecto**:
   ```
   C:\Users\Maria\OneDrive\Desktop\Universidad\TRABAJO DE GRADO 2\SGI-TCI-MK
   ```

2. **Crear base de datos MySQL**:
   ```sql
   CREATE DATABASE sgi_tci_mk;
   ```

3. **Configurar variables de entorno**:
   - Copiar `.env.example` a `.env`
   - Configurar las credenciales de MySQL:
     ```
     DB_HOST=localhost
     DB_PORT=3306
     DB_NAME=sgi_tci_mk
     DB_USER=root
     DB_PASSWORD=tu_contraseña
     SECRET_KEY=tu_clave_secreta
     ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Iniciar la aplicación

```bash
python run.py
```

El script `run.py` realizará automáticamente:
- Verificación de variables de entorno
- Verificación de conexión a PostgreSQL
- Inicialización de la base de datos (si es necesario)
- Creación de usuario administrador por defecto (si no existe)
- Inicio de la aplicación Flask

### Credenciales por defecto

- **Usuario**: admin
- **Contraseña**: admin123

⚠️ **IMPORTANTE**: Cambie la contraseña del administrador después del primer inicio de sesión.

## Estructura del Proyecto

```
SGI-TCI-MK/
├── app.py                  # Configuración principal de Flask
├── models.py               # Modelos SQLAlchemy
├── init_db.py             # Inicialización de base de datos
├── run.py                 # Script de inicio con verificaciones
├── requirements.txt       # Dependencias de Python
├── .env.example          # Plantilla de variables de entorno
├── routes/               # Rutas de la aplicación
│   ├── auth_routes.py    # Autenticación
│   ├── inventario_routes.py # Gestión de inventario
│   ├── ventas_routes.py  # Gestión de ventas
│   ├── egresos_routes.py # Gestión de egresos
│   └── reportes_routes.py # Reportes financieros
├── templates/            # Plantillas HTML
│   ├── base.html        # Plantilla base
│   ├── login.html       # Página de login
│   ├── dashboard.html   # Dashboard principal
│   ├── inventario.html  # Lista de productos
│   ├── inventario_form.html # Formulario de productos
│   ├── ventas.html      # Lista de ventas
│   ├── venta_form.html  # Formulario de ventas
│   ├── venta_detalle.html # Detalle de venta
│   ├── egresos.html     # Lista de egresos
│   ├── egreso_form.html # Formulario de egresos
│   ├── utilidad_diaria.html # Reporte de utilidad diaria
│   ├── cierre_caja.html # Formulario de cierre de caja
│   ├── historial_cierres.html # Historial de cierres
│   └── reporte_financiero.html # Reporte financiero
├── static/              # Archivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos personalizados
│   └── js/
│       └── main.js      # JavaScript principal
├── db/                  # Scripts de base de datos
│   └── sgi_tci_mk_der.sql
└── instance/            # Configuración local (convención Flask)
```

## Funcionalidades por Rol

### Administrador
- Gestión completa de inventario
- Gestión de egresos
- Acceso a todos los reportes financieros
- Cierre de caja
- Gestión de usuarios (futuro)

### Vendedor
- Registro de ventas
- Consulta de ventas propias
- Anulación de ventas propias
- Cierre de caja de turno

## Validaciones Implementadas

- **Backend**: Validación de formularios en Python
- **Frontend**: Validación en JavaScript para mejor experiencia de usuario
- **Stock**: Verificación de disponibilidad antes de confirmar ventas
- **Precios**: Validación que precio de venta > precio de costo
- **Roles**: Restricción de acceso por decoradores

## Seguridad

- Contraseñas hasheadas con werkzeug.security
- Sesiones gestionadas con Flask-Login
- Variables de entorno para credenciales de base de datos
- Sin hardcoding de credenciales

## Desarrollo

El proyecto está configurado para ejecutarse en modo desarrollo con `debug=True` en local. Para producción:

1. Cambiar `FLASK_DEBUG=False` en `.env`
2. Configurar un servidor WSGI como Gunicorn
3. Usar HTTPS
4. Configurar claves secretas robustas

## Soporte

Para problemas o preguntas, contacte al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Fecha**: Agosto 2026  
**Proyecto de Grado**: SGI-TCI MK
