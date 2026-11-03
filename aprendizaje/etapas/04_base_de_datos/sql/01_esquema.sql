-- =====================================================================
-- Etapa 04 - Esquema de la base de datos de Punto Lácteo (en 3FN)
--
-- Se puede ejecutar más de una vez: primero borra las tablas si existen.
-- Ejecutar:  source /sql/01_esquema.sql   (dentro del cliente mariadb)
-- =====================================================================

-- utf8mb4 guarda cualquier carácter Unicode (acentos, ñ, emojis).
ALTER DATABASE punto_lacteo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Se borran en orden inverso a las dependencias: primero las tablas que apuntan a otras.
DROP TABLE IF EXISTS venta_detalle;
DROP TABLE IF EXISTS venta;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS usuario;


-- Quién usa el sistema. El teléfono depende de la persona, no de cada venta (3FN).
CREATE TABLE usuario (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(80)  NOT NULL UNIQUE,
    telefono  VARCHAR(30)  NULL,
    rol       VARCHAR(20)  NOT NULL,
    CONSTRAINT ck_usuario_rol CHECK (rol IN ('duenio', 'empleado'))
);


-- Qué se vende. El precio de lista y el stock son del producto, no de cada venta (2FN).
CREATE TABLE producto (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    nombre  VARCHAR(80)    NOT NULL UNIQUE,
    unidad  VARCHAR(10)    NOT NULL,
    precio  DECIMAL(10, 2) NOT NULL,          -- hasta 99.999.999,99 con 2 decimales exactos
    stock   DECIMAL(10, 3) NOT NULL DEFAULT 0, -- kg con precisión de gramos, o unidades
    CONSTRAINT ck_producto_unidad CHECK (unidad IN ('kg', 'unidad')),
    CONSTRAINT ck_producto_precio CHECK (precio > 0),
    CONSTRAINT ck_producto_stock  CHECK (stock >= 0)
);


-- La cabecera de cada venta: cuándo y quién. Un usuario hace muchas ventas (1:N).
CREATE TABLE venta (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    fecha       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id  INT            NOT NULL,
    total       DECIMAL(12, 2) NOT NULL,       -- desnormalización consciente: ver módulo 04, sección 2.6
    CONSTRAINT fk_venta_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id)
);

-- Los reportes filtran por fecha: el índice evita recorrer toda la tabla.
CREATE INDEX idx_venta_fecha ON venta (fecha);


-- Las líneas de cada venta. Resuelve la relación N:M entre venta y producto.
CREATE TABLE venta_detalle (
    venta_id         INT            NOT NULL,
    producto_id      INT            NOT NULL,
    cantidad         DECIMAL(10, 3) NOT NULL,
    precio_unitario  DECIMAL(10, 2) NOT NULL,  -- el precio al momento de vender (historial)
    PRIMARY KEY (venta_id, producto_id),        -- un producto aparece una sola vez por venta
    CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
    -- Si se borra una venta, se borran sus líneas; un producto con ventas no se puede borrar.
    CONSTRAINT fk_detalle_venta    FOREIGN KEY (venta_id)    REFERENCES venta (id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto (id) ON DELETE RESTRICT
);
