-- Script SQL de referencia para SGI-TCI MK (Miscelánea Karen@)
-- Base de datos: MySQL 8.0
-- Versión: 4 - Con reglas de negocio y trazabilidad completa

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sgi_tci_mk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sgi_tci_mk;

-- Tabla: usuario
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('administrador','vendedor') NOT NULL,
    nombre_completo VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_cambio_password DATETIME DEFAULT CURRENT_TIMESTAMP,
    debe_cambiar_password BOOLEAN DEFAULT FALSE,
    INDEX idx_usuario_rol (rol),
    INDEX idx_usuario_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: producto
CREATE TABLE IF NOT EXISTS producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_precio_venta CHECK (precio_venta > precio_costo),
    CONSTRAINT chk_stock CHECK (stock_actual >= 0),
    INDEX idx_producto_activo (activo),
    INDEX idx_producto_stock (stock_actual, stock_minimo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: venta
CREATE TABLE IF NOT EXISTS venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('confirmada','anulada') DEFAULT 'confirmada',
    total DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    fecha_anulacion DATETIME,
    anulada_por INT,
    motivo_anulacion TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (anulada_por) REFERENCES usuario(id) ON DELETE SET NULL,
    INDEX idx_venta_usuario (usuario_id),
    INDEX idx_venta_fecha (fecha_hora),
    INDEX idx_venta_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: detalle_venta
CREATE TABLE IF NOT EXISTS detalle_venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES venta(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE RESTRICT,
    INDEX idx_detalle_venta_venta (venta_id),
    INDEX idx_detalle_venta_producto (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: egreso
CREATE TABLE IF NOT EXISTS egreso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50),
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL,
    INDEX idx_egreso_fecha (fecha_hora),
    INDEX idx_egreso_usuario (usuario_id),
    INDEX idx_egreso_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: cierre_caja
CREATE TABLE IF NOT EXISTS cierre_caja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo ENUM('turno','dia') DEFAULT 'dia',
    usuario_id INT NOT NULL,
    total_ventas DECIMAL(10,2) NOT NULL,
    total_egresos DECIMAL(10,2) NOT NULL,
    total_costos DECIMAL(10,2) NOT NULL,
    utilidad_real DECIMAL(10,2) NOT NULL,
    cantidad_ventas INT DEFAULT 0,
    fecha_hora_cierre DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE RESTRICT,
    UNIQUE KEY unique_cierre (fecha, tipo, usuario_id),
    INDEX idx_cierre_fecha (fecha),
    INDEX idx_cierre_usuario (usuario_id),
    INDEX idx_cierre_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migraciones para bases de datos existentes (si se aplican cambios)
-- Descomentar estas líneas si se está actualizando una base de datos existente

-- ALTER TABLE venta ADD COLUMN fecha_anulacion DATETIME;
-- ALTER TABLE venta ADD COLUMN anulada_por INT;
-- ALTER TABLE venta ADD COLUMN motivo_anulacion TEXT;
-- ALTER TABLE detalle_venta ADD COLUMN costo_unitario DECIMAL(10,2);
-- ALTER TABLE egreso ADD COLUMN activo BOOLEAN DEFAULT TRUE;
-- ALTER TABLE cierre_caja ADD COLUMN cantidad_ventas INT DEFAULT 0;
-- ALTER TABLE cierre_caja ADD CONSTRAINT unique_cierre UNIQUE (fecha, tipo, usuario_id);

-- Datos iniciales (comentados - se crean desde init_db.py)
-- INSERT INTO usuario (username, password_hash, rol, nombre_completo, activo, debe_cambiar_password) VALUES
-- ('admin', 'hashed_password_here', 'administrador', 'Administrador del Sistema', TRUE, TRUE),
-- ('vendedor', 'hashed_password_here', 'vendedor', 'Vendedor del Sistema', TRUE, TRUE);