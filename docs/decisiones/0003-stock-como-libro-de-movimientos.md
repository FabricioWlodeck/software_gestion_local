# 0003. Stock como libro de movimientos con saldo

- **Estado:** Aceptada
- **Fecha:** 2026-11-15 (MVP)

## Contexto

El stock lo modifican la dueña y los empleados en dos sucursales. Se vende por peso, se descarta mercadería y se corrigen diferencias al contar. La dueña quiere saber quién hizo cada cosa y por qué. Un dato que no se guarda no se puede reconstruir después.

## Opciones consideradas

1. **Columna que se sobrescribe.** Es lo más simple, pero solo guarda el valor actual.
2. **Libro de movimientos con saldo.** Cada cambio es una fila de `movimiento_stock` con tipo, cantidad con signo, saldo resultante, usuario, fecha, motivo y la venta, compra o traspaso que lo originó. La tabla `stock` guarda el saldo por producto y sucursal, y se actualiza en la misma transacción.
3. **Tabla versionada del sistema** (`WITH SYSTEM VERSIONING`). Guarda versiones de la fila, pero no el tipo de movimiento ni el motivo.

## Decisión

Se usa la opción 2. Las filas de `stock` se bloquean con `SELECT … FOR UPDATE`, en orden de `producto_id`, y restricciones `CHECK` controlan el signo por tipo de movimiento y que haya un motivo en las mermas, los ajustes y las anulaciones.

## Consecuencias

- El historial responde quién cargó, vendió, descartó o ajustó cada cantidad, y cuánto había en cualquier momento (`saldo_resultante`).
- Cada operación escribe dos cosas en la misma transacción. Un error de programación que actualice una sin la otra se detecta comparando el saldo con la suma de movimientos.
- Las mermas y los ajustes exigen un motivo en la pantalla.
- Los lotes con vencimiento (FEFO) quedaron fuera del MVP. Cuando se agreguen, cada movimiento apuntará además a un lote.
