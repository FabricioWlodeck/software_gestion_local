# 0004. El bot lee la base con un usuario de solo lectura y recibe los avisos por una tabla de salida

- **Estado:** Aceptada
- **Fecha:** 2026-11-15 (MVP)

## Contexto

El bot de Telegram tiene que avisarle a la dueña cuando el stock baja del mínimo, cuando se observa una venta, cuando hay una merma o un ajuste y cuando la caja cierra con diferencia, además de enviar resúmenes y responder consultas. En la materia IoT, el bot lee MariaDB directamente con aiomysql y la base tiene un usuario con permisos mínimos.

## Opciones consideradas

1. **El backend llama a la API de Telegram** en cada evento. Acopla las ventas a la disponibilidad de Telegram, y si Telegram falla, la venta tendría que fallar o perder el aviso.
2. **El bot consulta la API del backend.** Necesita un usuario y un token para el bot, y se aleja de la forma de trabajo de la materia.
3. **Tabla de salida (outbox) y lectura directa de la base.** El backend inserta el aviso en `notificacion` dentro de la misma transacción del evento, y el bot la consulta cada 30 segundos con un usuario que solo tiene `SELECT`.

## Decisión

Se usa la opción 3. Como el usuario del bot no puede escribir, el último aviso enviado se guarda en un archivo del volumen `datos_bot`. En el primer arranque se toma el último id existente, para no reenviar avisos viejos.

## Consecuencias

- Si la venta se descarta, su aviso también, porque está en la misma transacción. Si Telegram no responde, el aviso queda en la tabla y se envía después.
- El bot no puede modificar datos aunque su contraseña se filtre.
- Los avisos llegan con hasta 30 segundos de demora.
- Si se borra el volumen `datos_bot`, el bot vuelve a empezar desde el último aviso existente y no reenvía los anteriores.
