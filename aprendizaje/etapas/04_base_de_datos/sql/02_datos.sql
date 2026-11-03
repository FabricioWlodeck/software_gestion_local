-- =====================================================================
-- Etapa 04 - Datos de prueba (los de planilla_original.csv, ya normalizados)
-- Ejecutar después de 01_esquema.sql:  source /sql/02_datos.sql
-- =====================================================================

INSERT INTO usuario (id, nombre, telefono, rol) VALUES
    (1, 'Ana',   '555-0101', 'duenio'),
    (2, 'Bruno', '555-0102', 'empleado'),
    (3, 'Carla', '555-0103', 'empleado');

INSERT INTO producto (id, nombre, unidad, precio, stock) VALUES
    (1, 'Queso cremoso',     'kg',     12500.00,  1.750),
    (2, 'Leche entera 1 L',  'unidad',  1450.00, 21),
    (3, 'Salame milán',      'kg',     18900.00,  1.300),
    (4, 'Yogur bebible 1 L', 'unidad',  2300.00,  5),
    (5, 'Queso rallado 150 g', 'unidad', 3100.00, 0);   -- todavía no se vendió nunca

-- Las tres ventas de la planilla. El total se guarda calculado (ver 03_consultas.sql, consulta 6).
INSERT INTO venta (id, fecha, usuario_id, total) VALUES
    (1, '2026-11-02 09:15:00', 2, 7275.00),
    (2, '2026-11-02 10:40:00', 3, 3780.00),
    (3, '2026-11-02 11:05:00', 2, 3750.00);

INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario) VALUES
    (1, 1, 0.350, 12500.00),
    (1, 2, 2,      1450.00),
    (2, 3, 0.200, 18900.00),
    (3, 2, 1,      1450.00),
    (3, 4, 1,      2300.00);
