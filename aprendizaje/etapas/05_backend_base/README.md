# Etapa 05: backend ↔ base de datos

Esta etapa acompaña al módulo [05, backend ↔ base de datos](../../explicaciones_didacticas/05_backend_base.html). Es la etapa 03 con los datos en MariaDB: cambian los repositorios, los services (que ahora manejan la transacción) y las dependencias. **Los routers son idénticos.**

```
05_backend_base/
├── alembic.ini, alembic/      migraciones: versiones del esquema de la base
├── app/
│   ├── config.py              DATABASE_URL y opciones, desde variables de entorno
│   ├── database.py            engine, fábrica de sesiones y Base de los modelos
│   ├── models.py              las cuatro tablas como clases de SQLAlchemy
│   ├── semilla.py             carga usuarios y productos iniciales
│   ├── repositories/          SELECT, INSERT, UPDATE a través de la sesión
│   ├── services/              reglas del negocio y commit de cada operación
│   └── routers/ schemas/ ...  igual que en la etapa 03 (VentaIn suma usuario_id)
├── demo_concurrencia.py       dos cajas venden el mismo queso a la vez
└── ejemplos/                  cuerpos JSON para probar con curl.exe
```

## Preparación (una vez)

1. El contenedor `pl-mariadb` de la etapa 04 tiene que estar corriendo (`docker start pl-mariadb`).
2. Se crea una base nueva para esta etapa, así la de la etapa 04 queda intacta. Solo root puede crear bases:

```bash
docker exec pl-mariadb mariadb -u root -praiz123 -e "CREATE DATABASE IF NOT EXISTS punto_lacteo_orm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON punto_lacteo_orm.* TO 'pl'@'%';"
```

3. Con el entorno virtual activado, desde la carpeta `aprendizaje`:

```bash
pip install -r etapas/05_backend_base/requirements.txt
```

4. Desde la carpeta de esta etapa, se crean las tablas con la migración y se cargan los datos iniciales:

```bash
alembic upgrade head
```

```bash
python -m app.semilla
```

## Cómo se ejecuta

Desde la carpeta de esta etapa:

```bash
fastapi dev app/main.py
```

La terminal muestra cada consulta SQL que genera SQLAlchemy. Para ocultarlas: `$env:MOSTRAR_SQL = "0"` antes de arrancar.

## Cómo se prueba

```bash
curl.exe -i -X POST http://127.0.0.1:8000/ventas -H "Content-Type: application/json" --data-binary "@ejemplos/venta_valida.json"
```

Los demás archivos de `ejemplos/` prueban la venta sin stock (409), la fracción de un producto por unidad (422), el mismo producto repetido en dos líneas (se suman antes de validar) y la creación de un producto (`producto_nuevo.json`, 201 la primera vez y 409 la segunda).

La carrera entre dos cajas se prueba sin servidor. El script cambia el stock del queso:

```bash
python demo_concurrencia.py
```

## Comandos de Alembic

| Comando | Qué hace |
|---|---|
| `alembic upgrade head` | Aplica todas las migraciones pendientes |
| `alembic current` | Muestra en qué versión está la base |
| `alembic history` | Lista las migraciones |
| `alembic downgrade -1` | Deshace la última migración (¡borra lo que creó!) |
| `alembic revision --autogenerate -m "descripción"` | Compara los modelos con la base y escribe una migración nueva, que hay que revisar antes de aplicar |

## Qué observar

1. Los routers no cambiaron respecto de la etapa 03, aunque los datos ahora estén en MariaDB.
2. En la terminal del servidor, una venta válida termina en `COMMIT` y una rechazada en `ROLLBACK`.
3. Las fechas que guarda MariaDB están en UTC (la hora del contenedor), 3 horas adelante de la hora local de la PC (UTC−3).
