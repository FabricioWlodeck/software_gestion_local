# Etapa 01: HTTP a mano

Esta etapa acompaña al módulo [01, HTTP y REST](../../explicaciones_didacticas/01_http_rest.html). Es un servidor HTTP escrito con la biblioteca estándar de Python, sin FastAPI, para ver qué llega y qué sale por la red sin ninguna capa intermedia. No hace falta instalar nada.

| Archivo | Qué hace |
|---|---|
| `servidor.py` | Atiende `GET`, `POST` y `DELETE` sobre `/productos` e imprime cada petición y cada respuesta completas |
| `cliente.py` | Envía los siete casos del módulo y muestra cada respuesta tal como llega |
| `ejemplos/*.json` | Cuerpos de ejemplo para probar con `curl.exe` |

## Cómo se ejecuta

Hacen falta dos terminales abiertas en esta carpeta.

En la primera terminal se levanta el servidor, que queda esperando peticiones:

```bash
python servidor.py
```

En la segunda terminal se ejecuta el cliente, que hace una pausa entre caso y caso:

```bash
python cliente.py
```

Conviene mirar las dos terminales a la vez. El cliente muestra la respuesta, y el servidor muestra la petición completa tal como llegó, incluidos los headers que agrega la librería por su cuenta.

Para detener el servidor se usa `Ctrl+C`. Los productos viven en memoria, así que al reiniciar el servidor vuelven a ser los tres originales.

## Otras formas de probar

El navegador solo puede hacer peticiones `GET` desde la barra de direcciones. Abriendo <http://127.0.0.1:8000/productos> se ve la lista en JSON.

`curl.exe` viene incluido en Windows y permite enviar cualquier método. En PowerShell se escribe `curl.exe` y no `curl`, porque en Windows PowerShell `curl` es un alias de otro comando. La opción `-i` muestra también la línea de estado y los headers de la respuesta.

```bash
curl.exe -i http://127.0.0.1:8000/productos/1
```

```bash
curl.exe -i -X POST http://127.0.0.1:8000/productos -H "Content-Type: application/json" --data-binary "@ejemplos/producto_valido.json"
```

```bash
curl.exe -i -X DELETE http://127.0.0.1:8000/productos/3 -H "Authorization: Bearer token-de-prueba-123"
```

## Qué observar

1. La petición del caso 3 tiene un header `Content-Length` que nadie escribió a mano. Lo calcula `http.client` a partir del cuerpo.
2. La respuesta 201 trae un header `Location` que indica dónde quedó el producto nuevo.
3. La respuesta 204 no tiene cuerpo ni `Content-Length`.
4. Si se ejecuta `cliente.py` dos veces sin reiniciar el servidor, el caso 6 responde 404 la segunda vez, porque el producto 2 ya no existe. El estado final es el mismo que tras la primera ejecución. Eso es lo que significa que `DELETE` sea idempotente.
