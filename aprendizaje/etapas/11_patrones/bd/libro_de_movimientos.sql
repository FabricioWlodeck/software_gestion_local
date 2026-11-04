-- =====================================================================
-- Etapa 11 - Libro de movimientos para el stock
--
-- Compara dos formas de guardar el stock con los mismos hechos de una semana:
--   A. Una columna que se sobrescribe (producto.stock, como en las etapas 04 a 10).
--   B. Un libro de movimientos: cada cambio es una fila nueva, con quién, cuándo y por qué.
-- Cada hecho se registra de las dos formas dentro de una transacción. El UPDATE es lo
-- único que guardaría la forma A; el INSERT es lo que agrega la forma B.
--
-- Ejecutar (ver README.md):  source /tmp/libro_de_movimientos.sql
-- Se puede ejecutar varias veces: empieza borrando las tablas.
-- =====================================================================

DROP TABLE IF EXISTS movimiento_stock;
DROP TABLE IF EXISTS producto;

CREATE TABLE producto (
    id      INT            PRIMARY KEY,
    nombre  VARCHAR(80)    NOT NULL,
    unidad  VARCHAR(10)    NOT NULL,
    stock   DECIMAL(10, 3) NOT NULL DEFAULT 0,  -- forma A: un solo número, sin historia
    CONSTRAINT ck_producto_unidad CHECK (unidad IN ('kg', 'unidad'))
);

CREATE TABLE movimiento_stock (
    id           INT            AUTO_INCREMENT PRIMARY KEY,
    producto_id  INT            NOT NULL,
    tipo         VARCHAR(10)    NOT NULL,
    cantidad     DECIMAL(10, 3) NOT NULL,  -- con signo: positiva entra, negativa sale
    usuario      VARCHAR(40)    NOT NULL,  -- en el sistema real, usuario_id con FK a usuario
    motivo       VARCHAR(120)   NULL,      -- obligatorio para ajustes y mermas (ver CHECK)
    fecha        DATETIME       NOT NULL,
    CONSTRAINT fk_movimiento_producto FOREIGN KEY (producto_id) REFERENCES producto (id),
    -- El signo depende del tipo: una compra solo puede sumar y una venta solo puede restar.
    CONSTRAINT ck_movimiento_signo CHECK (
        (tipo = 'compra' AND cantidad > 0)
        OR (tipo IN ('venta', 'merma') AND cantidad < 0)
        OR (tipo = 'ajuste' AND cantidad <> 0)
    ),
    CONSTRAINT ck_movimiento_motivo CHECK (tipo IN ('compra', 'venta') OR motivo IS NOT NULL),
    INDEX idx_movimiento_producto_fecha (producto_id, fecha)
);

INSERT INTO producto (id, nombre, unidad) VALUES
    (1, 'Queso cremoso', 'kg'),
    (2, 'Leche entera 1 L', 'unidad');

-- ---------------------------------------------------------------------
-- Los hechos de la semana, en orden
-- ---------------------------------------------------------------------

-- Lunes 08:10: llega la compra.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'compra', 5.000, 'Ana', 'Remito 0012', '2026-11-02 08:10'),
    (2, 'compra', 24, 'Ana', 'Remito 0012', '2026-11-02 08:10');
UPDATE producto SET stock = stock + 5.000 WHERE id = 1;
UPDATE producto SET stock = stock + 24 WHERE id = 2;
COMMIT;

-- Lunes 10:32: Bruno cobra queso y leche.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'venta', -0.350, 'Bruno', 'Venta 1', '2026-11-02 10:32'),
    (2, 'venta', -2, 'Bruno', 'Venta 1', '2026-11-02 10:32');
UPDATE producto SET stock = stock - 0.350 WHERE id = 1;
UPDATE producto SET stock = stock - 2 WHERE id = 2;
COMMIT;

-- Lunes 17:05: Bruno cobra más queso.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'venta', -1.200, 'Bruno', 'Venta 2', '2026-11-02 17:05');
UPDATE producto SET stock = stock - 1.200 WHERE id = 1;
COMMIT;

-- Martes 09:15: Carla cobra queso y leche.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'venta', -0.500, 'Carla', 'Venta 3', '2026-11-03 09:15'),
    (2, 'venta', -6, 'Carla', 'Venta 3', '2026-11-03 09:15');
UPDATE producto SET stock = stock - 0.500 WHERE id = 1;
UPDATE producto SET stock = stock - 6 WHERE id = 2;
COMMIT;

-- Martes 19:40: al cerrar, Carla pesa el queso y corrige el stock.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'ajuste', -2.000, 'Carla', 'Conteo de cierre', '2026-11-03 19:40');
UPDATE producto SET stock = stock - 2.000 WHERE id = 1;
COMMIT;

-- Miércoles 08:30: Ana descarta una parte vencida.
START TRANSACTION;
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha) VALUES
    (1, 'merma', -0.250, 'Ana', 'Vencido', '2026-11-04 08:30');
UPDATE producto SET stock = stock - 0.250 WHERE id = 1;
COMMIT;

-- ---------------------------------------------------------------------
-- Lo que responde cada forma
-- ---------------------------------------------------------------------

-- 1. Forma A: el stock es un número. Se compraron 5 kg de queso y se vendieron 2,050 kg,
--    pero quedan 0,700 kg. La columna no puede explicar la diferencia.
SELECT nombre, unidad, stock
FROM producto
ORDER BY id;

-- 2. Forma B: el stock es la suma de los movimientos, y coincide con la columna.
SELECT p.nombre, SUM(m.cantidad) AS stock_calculado, p.stock AS stock_en_columna
FROM producto AS p
JOIN movimiento_stock AS m ON m.producto_id = p.id
GROUP BY p.id, p.nombre, p.stock
ORDER BY p.id;

-- 3. Historial del queso con el saldo después de cada movimiento (función de ventana).
SELECT fecha, tipo, cantidad, usuario,
       SUM(cantidad) OVER (ORDER BY fecha, id) AS saldo
FROM movimiento_stock
WHERE producto_id = 1
ORDER BY fecha, id;

-- 4. ¿Dónde está la diferencia? Lo que salió sin venderse, con quién y por qué.
SELECT fecha, tipo, cantidad, usuario, motivo
FROM movimiento_stock
WHERE producto_id = 1 AND tipo IN ('ajuste', 'merma')
ORDER BY fecha;

-- 5. ¿Cuánto queso había el martes al mediodía? Con la columna, ese dato ya no existe.
SELECT SUM(cantidad) AS stock_martes_12
FROM movimiento_stock
WHERE producto_id = 1 AND fecha <= '2026-11-03 12:00';

-- 6. Las restricciones protegen el libro: una venta con cantidad positiva y un ajuste
--    sin motivo se rechazan. Con --force, el script sigue después de cada error.
INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha)
VALUES (1, 'venta', 0.500, 'Bruno', 'Venta 4', '2026-11-04 10:00');

INSERT INTO movimiento_stock (producto_id, tipo, cantidad, usuario, motivo, fecha)
VALUES (1, 'ajuste', -0.100, 'Bruno', NULL, '2026-11-04 10:05');
