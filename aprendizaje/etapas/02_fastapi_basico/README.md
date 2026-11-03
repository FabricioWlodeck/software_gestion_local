# Etapa 02: FastAPI desde cero

Esta etapa acompaña al módulo [02, FastAPI desde cero](../../explicaciones_didacticas/02_fastapi_basico.html). Es la misma API de la etapa 01 (mismas rutas, mismos campos), escrita con FastAPI en un solo archivo. El archivo `main.py` tiene 89 líneas, contra las 189 de `servidor.py`.

## Entorno virtual (una sola vez para todo el aprendizaje)

Las etapas 02, 03, 05 y 06 comparten un entorno virtual en `aprendizaje/.venv`, que git ignora. Desde la carpeta `aprendizaje`:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\Activate.ps1
```

Si PowerShell responde que «la ejecución de scripts está deshabilitada», hay dos salidas. La primera es habilitar los scripts firmados o locales para tu usuario con `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, que es una decisión de configuración de tu PC. La segunda es no activar el entorno y llamar a sus programas con la ruta completa, por ejemplo `.venv\Scripts\fastapi.exe dev main.py`.

Con el entorno activado, el prompt empieza con `(.venv)`. Se instala lo de esta etapa:

```bash
pip install -r etapas/02_fastapi_basico/requirements.txt
```

## Cómo se ejecuta

Desde la carpeta de esta etapa, con el entorno activado:

```bash
fastapi dev main.py
```

`fastapi dev` levanta Uvicorn en <http://127.0.0.1:8000> y lo reinicia cada vez que se guarda un cambio en el código. Al reiniciarse, los productos creados se pierden, porque viven en memoria.

## Cómo se prueba

| Forma | Qué se ve |
|---|---|
| <http://127.0.0.1:8000/docs> | La documentación interactiva. Con «Try it out» se puede enviar cualquier petición desde el navegador. |
| <http://127.0.0.1:8000/openapi.json> | El contrato de la API en formato OpenAPI, generado a partir del código. |
| `python ../01_http/cliente.py` (desde esta carpeta) | Los mismos siete casos del módulo 01, ahora contra FastAPI. |
| `curl.exe -i http://127.0.0.1:8000/productos/abc` | El error 422 que genera FastAPI cuando un parámetro no tiene el tipo declarado. |

## Qué observar

1. Con `cliente.py`, todos los casos responden igual que en la etapa 01 salvo el 4: FastAPI responde 422 y detalla cada campo inválido en una lista.
2. Los headers de la respuesta llegan en minúsculas (`content-type`). En HTTP/1.1 los nombres de los headers no distinguen mayúsculas.
3. El JSON de FastAPI no tiene espacios y el `id` aparece al final, porque `ProductoOut` hereda los campos de `ProductoIn` y después agrega el suyo. En JSON el orden de las claves no tiene significado.
