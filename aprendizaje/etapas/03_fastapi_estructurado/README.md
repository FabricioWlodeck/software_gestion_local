# Etapa 03: FastAPI estructurado

Esta etapa acompaña al módulo [03, FastAPI estructurado](../../explicaciones_didacticas/03_fastapi_estructurado.html). La API de productos de la etapa 02 se divide en capas y se agregan las ventas, con control de stock. Los datos siguen en memoria; el módulo 05 los pasa a MariaDB cambiando solo los repositorios.

```
03_fastapi_estructurado/
├── app/
│   ├── main.py            crea la app, suma los routers y traduce errores a HTTP
│   ├── config.py          configuración (variables de entorno con valor por defecto)
│   ├── errores.py         errores de las reglas del negocio
│   ├── dependencies.py    construye services y repositories para cada ruta
│   ├── routers/           HTTP ↔ service
│   ├── schemas/           forma de los datos que entran y salen
│   ├── services/          reglas del negocio
│   └── repositories/      guardar y buscar datos (por ahora en memoria)
├── probar_service.py      usa el service de ventas sin HTTP
└── ejemplos/              cuerpos JSON para probar con curl.exe
```

## Cómo se ejecuta

Con el entorno virtual de `aprendizaje/.venv` activado (ver la etapa 02), **desde la carpeta de esta etapa**:

```bash
fastapi dev app/main.py
```

Se ejecuta desde acá y no desde `app/` porque el código importa con rutas absolutas (`from app.services...`), y Python tiene que poder encontrar la carpeta `app`.

## Cómo se prueba

El service se puede usar sin servidor:

```bash
python probar_service.py
```

Con el servidor levantado, desde otra terminal en esta carpeta:

```bash
curl.exe -i -X POST http://127.0.0.1:8000/ventas -H "Content-Type: application/json" --data-binary "@ejemplos/venta_valida.json"
```

```bash
curl.exe -i -X POST http://127.0.0.1:8000/ventas -H "Content-Type: application/json" --data-binary "@ejemplos/venta_sin_stock.json"
```

```bash
curl.exe -i -X POST http://127.0.0.1:8000/ventas -H "Content-Type: application/json" --data-binary "@ejemplos/venta_cantidad_invalida.json"
```

También se puede probar todo desde <http://127.0.0.1:8000/docs>, donde las rutas aparecen agrupadas por `tags`.

## Qué observar

1. La venta válida responde 201 con el total calculado: 0,350 kg × $12.500 + 2 × $1.450 = $7.275.
2. Después de esa venta, la de 3 kg responde 409, porque quedan 1,750 kg de queso.
3. «1,5 leches» responde 422 desde el service, no desde Pydantic: el schema no puede saber que la leche se vende por unidad, porque eso depende del producto.
4. Si se ejecuta `python ../01_http/cliente.py`, el caso 3 ahora responde 422, porque `ProductoIn` exige el campo `stock`. Cambiar un schema de entrada cambia el contrato y rompe a los clientes que no lo conocen.
