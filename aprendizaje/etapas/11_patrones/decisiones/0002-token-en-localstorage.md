# 0002. Guardar el token de sesión en localStorage

- **Estado:** Aceptada para el material de aprendizaje; a revisar en el proyecto real
- **Fecha:** 2026-11-03 (módulos 06 y 09)

## Contexto

El backend identifica a cada usuario con un token JWT (JSON Web Token) que el frontend envía en el header `Authorization: Bearer`. El frontend tiene que guardar ese token en algún lugar entre una petición y la siguiente, y la cajera no debería tener que iniciar sesión cada vez que recarga la página.

## Opciones consideradas

1. **En memoria** (una variable de JavaScript). Ningún otro script lo encuentra guardado, pero se pierde al recargar.
2. **En `localStorage`.** Sobrevive a las recargas y se envía de forma explícita, así que el mecanismo se ve completo. Cualquier script que se ejecute en la página puede leerlo.
3. **En una cookie `httpOnly`.** JavaScript no puede leerla y el navegador la envía sola. Exige protegerse de CSRF (Cross-Site Request Forgery o Falsificación de Peticiones en Sitios Cruzados) y configurar la cookie en el backend.

## Decisión

Se guarda en `localStorage`, con la clave `punto-lacteo.token`.

## Consecuencias

- La sesión sobrevive a las recargas y el código del cliente de la API es corto.
- Un ataque XSS (Cross-Site Scripting o Secuencia de Comandos en Sitios Cruzados) podría leer el token. Lo mitigan que React escapa el texto por defecto, que el código no usa `dangerouslySetInnerHTML`, que el token vence a las 8 horas y que en producción se sirve por HTTPS.
- Si el sistema queda expuesto a internet, conviene reemplazar esta decisión por la opción 3 con un registro nuevo.
