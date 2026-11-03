-- =====================================================================
-- Etapa 04 - Cada sentencia de este archivo DEBE fallar.
-- Muestran que la base rechaza datos inválidos aunque el backend tenga un error.
-- Ejecutar con --force para que siga después de cada error:
--   mariadb ... --force -e "source /sql/04_restricciones.sql"
-- =====================================================================

-- CHECK: un precio no puede ser negativo.
INSERT INTO producto (nombre, unidad, precio) VALUES ('Manteca 200 g', 'unidad', -10);

-- CHECK: la unidad solo puede ser 'kg' o 'unidad'.
INSERT INTO producto (nombre, unidad, precio) VALUES ('Crema 350 ml', 'litro', 2500);

-- UNIQUE: no puede haber dos productos con el mismo nombre.
INSERT INTO producto (nombre, unidad, precio) VALUES ('Queso cremoso', 'kg', 13000);

-- FOREIGN KEY: no se puede vender un producto que no existe.
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario) VALUES (1, 99, 1, 100);

-- PRIMARY KEY compuesta: el mismo producto no puede repetirse en una venta.
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario) VALUES (1, 1, 1.500, 12500);

-- ON DELETE RESTRICT: no se puede borrar un producto que ya tiene ventas.
DELETE FROM producto WHERE id = 1;

-- CHECK: el stock no puede quedar negativo.
UPDATE producto SET stock = stock - 5 WHERE id = 3;
