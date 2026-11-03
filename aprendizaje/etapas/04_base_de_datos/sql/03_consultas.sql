-- =====================================================================
-- Etapa 04 - Consultas que responden preguntas reales del negocio
-- Ejecutar:  source /sql/03_consultas.sql
-- =====================================================================

-- 1. ¿Qué productos tienen poco stock? (lo que el bot avisaría)
SELECT nombre, unidad, stock
FROM producto
WHERE stock < 2
ORDER BY stock;

-- 2. ¿Qué ventas hubo el 2 de noviembre y quién las cobró? (JOIN entre venta y usuario)
SELECT v.id, v.fecha, u.nombre AS cajera, v.total
FROM venta AS v
JOIN usuario AS u ON u.id = v.usuario_id
WHERE v.fecha >= '2026-11-02' AND v.fecha < '2026-11-03'
ORDER BY v.fecha;

-- 3. ¿Qué se vendió en la venta 1? (JOIN entre detalle y producto)
SELECT p.nombre, d.cantidad, p.unidad, d.precio_unitario,
       ROUND(d.cantidad * d.precio_unitario, 2) AS subtotal
FROM venta_detalle AS d
JOIN producto AS p ON p.id = d.producto_id
WHERE d.venta_id = 1;

-- 4. ¿Cuánto se vendió de cada producto? (GROUP BY con funciones de agregación)
SELECT p.nombre, SUM(d.cantidad) AS cantidad_vendida, p.unidad,
       SUM(ROUND(d.cantidad * d.precio_unitario, 2)) AS recaudado
FROM venta_detalle AS d
JOIN producto AS p ON p.id = d.producto_id
GROUP BY p.id, p.nombre, p.unidad
ORDER BY recaudado DESC;

-- 5. ¿Cuánto cobró cada persona?
SELECT u.nombre, COUNT(v.id) AS ventas, COALESCE(SUM(v.total), 0) AS total_cobrado
FROM usuario AS u
LEFT JOIN venta AS v ON v.usuario_id = u.id
GROUP BY u.id, u.nombre
ORDER BY total_cobrado DESC;

-- 6. ¿El total guardado coincide con la suma de las líneas? (control de la desnormalización)
SELECT v.id, v.total AS total_guardado,
       SUM(ROUND(d.cantidad * d.precio_unitario, 2)) AS total_calculado
FROM venta AS v
JOIN venta_detalle AS d ON d.venta_id = v.id
GROUP BY v.id, v.total
HAVING total_guardado <> total_calculado;   -- sin filas = todo coincide
