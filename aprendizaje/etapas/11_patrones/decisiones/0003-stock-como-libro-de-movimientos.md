# 0003. Stock como libro de movimientos con saldo

- **Estado:** Propuesta (se decide al diseñar el MVP, junto con los lotes y vencimientos)
- **Fecha:** 2026-11-04 (módulo 11)

## Contexto

En las etapas 04 a 10, el stock es una columna (`producto.stock`) que cada venta sobrescribe. En el local, el stock lo cargan la dueña y los empleados, se vende por peso, se descarta mercadería vencida y se pesa la horma al cerrar. La dueña quiere saber quién hizo cada cosa. Con una columna, si el stock no coincide con lo vendido, no hay forma de saber por qué, y un dato que no se guardó no se puede reconstruir después.

## Opciones consideradas

1. **Columna que se sobrescribe.** Es lo más simple, pero solo guarda el valor actual.
2. **Libro de movimientos con saldo.** Cada cambio es una fila de `movimiento_stock` con tipo, cantidad con signo, usuario, fecha y motivo. La columna `producto.stock` se mantiene como saldo y se actualiza en la misma transacción.
3. **Tabla versionada del sistema** (`WITH SYSTEM VERSIONING` de MariaDB). Guarda cada versión de la fila sin escribir código, pero no registra el tipo de movimiento ni el motivo.
4. **Event sourcing completo.** Todo el estado del sistema se reconstruye a partir de eventos. Es más de lo que el proyecto necesita.

## Decisión

Se propone la opción 2.

## Consecuencias

- Se puede responder quién cargó o ajustó cada cantidad, cuánto había en cualquier fecha y dónde está una diferencia (consultas 3 a 5 de `bd/libro_de_movimientos.sql`).
- Cada operación que cambia el stock escribe dos cosas, y las dos tienen que ir en la misma transacción.
- Conviene una consulta de control periódica que compare el saldo con la suma de movimientos.
- Los ajustes y las mermas exigen un motivo, lo que agrega un campo a esas pantallas.
