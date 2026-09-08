# SGI-TCI MK - Sistema de Gestión de Inventario y Trazabilidad de Costos e Ingresos

Sistema web para la gestión de inventario, ventas y trazabilidad financiera de la Miscelánea Karen@.

## Características (Versión 3)

### Gestión de Negocio
- **Gestión de Inventario**: Registro, actualización, consulta y desactivación de productos
- **Gestión de Ventas**: Registro de ventas con cálculo automático de totales y descuento de stock
- **Anulación de Ventas**: Reversión de stock al anular ventas
- **Gestión de Gastos**: Registro y consulta de egresos del negocio (renombrado de "Egresos")
- **Reportes Financieros**: 
  - Utilidad diaria (ingresos - costos - gastos)
  - Cierre de caja diario (administrador) y cierre de turno (vendedor)
  - Reportes financieros por período
  - Pantalla intermedia de reportes con explicaciones claras

### Seguridad y Usuarios
- **Política de Contraseñas**: 
  - Mínimo 8 caracteres
  - Al menos un carácter especial (@ + / *)
  - Combinación de letras y números
  - No puede contener el nombre de usuario
  - Cambio obligatorio cada 6 meses
- **Gestión de Usuarios**: CRUD completo de usuarios
- **Restablecimiento de Contraseñas**: Función para administradores
- **Roles y Permisos**: 
  - Rol Administrador: acceso completo
  - Rol Vendedor: acceso a ventas y cierre de turno

### Interfaz de Usuario
- **Identidad Visual**: Paleta de colores propia (azul #014886, dorado #B28C3D, gris #7E778C)
- **Navegación Simplificada**: Menú adaptado por rol sin submenús complejos
- **Lenguaje del Negocio**: Términos claros para usuarios no técnicos
- **Validación Visual**: Checklist de requisitos de contraseña en tiempo real
- **Mensajes Claros**: Feedback en primera persona del plural

### Despliegue
- **Desarrollo Local**: Configurado para Windows 11 con MySQL
- **Producción**: Configurado para Railway con Procfile y Gunicorn
- **Variables de Entorno**: Gestión segura de credenciales

## Requisitos

- Python 3.8+
- MySQL 8.0+
- Windows 11 (desarrollo local)
- Railway (producción)

## Instalación Local

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
     FLASK_DEBUG=True
     ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Aplicar migraciones (si se actualiza desde versión anterior)**:
   ```bash
   python migrar_db.py
   python actualizar_usuarios.py
   ```

## Uso

### Iniciar la aplicación

```bash
python run.py
```

El script `run.py` realizará automáticamente:
- Verificación de variables de entorno
- Verificación de conexión a MySQL
- Inicialización de la base de datos (si es necesario)
- Creación de usuarios por defecto (si no existen)
- Inicio de la aplicación Flask

### Credenciales por defecto (Versión 3)

⚠️ **IMPORTANTE**: El sistema exige cambiar estas contraseñas en el primer inicio de sesión.

- **Administrador**:
  - Usuario: `admin`
  - Contraseña: `Admin@2026`
  - Rol: acceso completo

- **Vendedor**:
  - Usuario: `vendedor`
  - Contraseña: `Venta*2026`
  - Rol: ventas y cierre de turno

## Despliegue en Railway

### 1. Preparar el repositorio

```bash
# Asegurarse de que .gitignore esté configurado correctamente
git init
git add .
git commit -m "Implementación SGI-TCI MK v3"
```

### 2. Crear proyecto en Railway

1. Crear cuenta en [Railway](https://railway.app)
2. Crear nuevo proyecto
3. Conectar repositorio GitHub

### 3. Configurar servicios

**Servicio MySQL**:
- Agregar plugin MySQL
- Railway generará automáticamente las variables de conexión

**Servicio Web**:
- Configurar variables de entorno:
  ```
  DB_HOST=${{MySQL.MYSQLHOST}}
  DB_PORT=${{MySQL.MYSQLPORT}}
  DB_NAME=${{MySQL.MYSQLDATABASE}}
  DB_USER=${{MySQL.MYSQLUSER}}
  DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
  SECRET_KEY=<cadena_aleatoria_32+>
  FLASK_DEBUG=False
  ```

### 4. Inicializar base de datos en producción

```bash
# Desde la consola del servicio web en Railway
python init_db.py
```

### 5. Verificar despliegue

- Railway asignará una URL pública
- La aplicación estará disponible en la URL asignada

## Estructura del Proyecto

```
SGI-TCI-MK/
├── app.py                  # Configuración principal de Flask
├── models.py               # Modelos SQLAlchemy actualizados
├── init_db.py             # Inicialización de base de datos v3
├── run.py                 # Script de inicio local
├── migrar_db.py           # Script de migración para actualizaciones
├── actualizar_usuarios.py # Script para actualizar contraseñas
├── Procfile               # Configuración de Railway
├── runtime.txt            # Versión de Python para Railway
├── .gitignore             # Archivos a ignorar en Git
├── requirements.txt       # Dependencias (incluye gunicorn)
├── .env.example          # Plantilla de variables de entorno
├── utils/                # Utilidades del sistema
│   ├── seguridad.py      # Validación de contraseñas y seguridad
│   └── formato.py        # Filtros Jinja personalizados
├── routes/               # Rutas de la aplicación
│   ├── auth_routes.py    # Autenticación, usuarios, cambio de contraseña
│   ├── inventario_routes.py # Gestión de inventario
│   ├── ventas_routes.py  # Gestión de ventas
│   ├── egresos_routes.py # Gestión de gastos
│   └── reportes_routes.py # Reportes financieros y cierres
├── templates/            # Plantillas HTML actualizadas
│   ├── base.html        # Plantilla base con navegación por rol
│   ├── login.html       # Página de login
│   ├── cambiar_password.html # Formulario de cambio de contraseña
│   ├── dashboard.html   # Dashboard adaptado por rol
│   ├── reportes_menu.html # Pantalla intermedia de reportes
│   ├── cierre_resumen.html # Resumen imprimible de cierres
│   ├── inventario.html  # Lista de productos
│   ├── inventario_form.html # Formulario de productos
│   ├── ventas.html      # Lista de ventas
│   ├── venta_form.html  # Formulario de ventas
│   ├── venta_detalle.html # Detalle de venta
│   ├── egresos.html     # Lista de gastos
│   ├── egreso_form.html # Formulario de gastos
│   ├── utilidad_diaria.html # Reporte de utilidad diaria
│   ├── cierre_caja.html # Formulario de cierre de caja
│   ├── historial_cierres.html # Historial de cierres
│   ├── reporte_financiero.html # Reporte financiero
│   ├── usuarios.html    # Gestión de usuarios
│   └── usuario_form.html # Formulario de usuarios
├── static/              # Archivos estáticos
│   ├── css/
│   │   └── style.css    # Estilos con paleta propia
│   └── js/
│       └── main.js      # JavaScript principal
├── db/                  # Scripts de base de datos
│   └── sgi_tci_mk_actualizado.sql # SQL de referencia v3
└── instance/            # Configuración local (convención Flask)
```

## Funcionalidades por Rol

### Administrador
- Gestión completa de inventario
- Gestión de gastos (antes "egresos")
- Acceso a todos los reportes financieros
- Cierre de caja del día
- Gestión de usuarios (CRUD completo)
- Restablecimiento de contraseñas
- Dashboard con estadísticas completas

### Vendedor
- Registro de ventas propias
- Consulta de ventas propias
- Anulación de ventas propias
- Cierre de caja de turno (solo sus ventas del día)
- Dashboard con estadísticas limitadas
- Menú simplificado: Inicio · Ventas · Cierre de caja · Cerrar sesión

## Validaciones Implementadas

### Backend
- Validación de formularios en Python
- Política de contraseñas en todas las rutas relevantes
- Verificación de disponibilidad de stock
- Validación que precio de venta > precio de costo
- Restricción de acceso por decoradores
- Rollback de transacciones ante errores

### Frontend
- Validación de formularios en JavaScript
- Checklist visual de requisitos de contraseña
- Cálculos automáticos en tiempo real
- Modales de confirmación para acciones irreversibles
- Feedback inmediato al usuario

## Seguridad

- **Contraseñas**: Hasheadas con werkzeug.security
- **Política de contraseñas**: Reglas estrictas con cambio periódico
- **Sesiones**: Gestionadas con Flask-Login
- **Variables de entorno**: Credenciales no hardcodeadas
- **Validación de vencimiento**: Sistema alerta y fuerza cambio de contraseña
- **Codificación**: UTF-8 para soporte de caracteres especiales

## Identidad Visual

### Paleta de Colores
- **Azul principal**: `#014886` - navegación, botones primarios, enlaces
- **Dorado**: `#B28C3D` - acentos, totales, acciones principales
- **Gris**: `#7E778C` - texto secundario, bordes, elementos auxiliares
- **Fondo**: `#FAFAFA` - fondo general de la aplicación

### Reglas de Diseño
- Navegación diferenciada por rol (vendedor con franja dorada)
- Botones con altura mínima de 44px para accesibilidad
- Tipografía system-ui para mejor rendimiento
- Diseño responsivo con Bootstrap 5

## Desarrollo

### Modo Desarrollo Local
```bash
python run.py
```

### Modo Producción (Railway)
- Despliegue automático desde GitHub
- Servidor Gunicorn configurado en Procfile
- Variables de entorno gestionadas por Railway
- Base de datos MySQL gestionada por Railway

## Soporte

Para problemas o preguntas, consulte la documentación detallada en `PROMPT_IMPLEMENTACION_ACTUALIZADO.md`.

---

**Versión**: 3.0.0  
**Fecha**: Septiembre 2026  
**Proyecto de Grado**: SGI-TCI MK  
**Tecnologías**: Flask, MySQL, Bootstrap 5, Railway
