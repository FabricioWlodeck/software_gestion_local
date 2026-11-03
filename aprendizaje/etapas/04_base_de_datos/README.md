# Etapa 04: diseño de la base de datos

Esta etapa acompaña al módulo [04, diseño de la base de datos](../../explicaciones_didacticas/04_base_de_datos.html). No tiene código Python: es la base de datos de Punto Lácteo escrita a mano en SQL, para ver qué hay debajo antes de usar SQLAlchemy en el módulo 05.

| Archivo | Qué hace |
|---|---|
| `planilla_original.csv` | La planilla de ventas desnormalizada de la que parte el módulo |
| `sql/01_esquema.sql` | Crea las cuatro tablas normalizadas, con sus claves y restricciones |
| `sql/02_datos.sql` | Carga las ventas de la planilla, ya normalizadas |
| `sql/03_consultas.sql` | Seis consultas que responden preguntas del negocio |
| `sql/04_restricciones.sql` | Siete sentencias que deben fallar, una por cada restricción |

## 1. Levantar MariaDB en un contenedor

Docker Desktop tiene que estar abierto. Desde la carpeta de esta etapa, en PowerShell:

```bash
docker run -d --name pl-mariadb -e MARIADB_ROOT_PASSWORD=raiz123 -e MARIADB_DATABASE=punto_lacteo -e MARIADB_USER=pl -e MARIADB_PASSWORD=pl123 -p 3307:3306 -v pl-datos:/var/lib/mysql -v "${PWD}\sql:/sql:ro" mariadb:11.4
```

| Parte del comando | Qué hace |
|---|---|
| `-d` | Deja el contenedor corriendo en segundo plano |
| `--name pl-mariadb` | Le da un nombre para referirse a él en los demás comandos |
| `-e MARIADB_...` | Variables de entorno que la imagen usa en el primer arranque: contraseña de root, base a crear y un usuario con permisos sobre ella |
| `-p 3307:3306` | Publica el puerto 3306 del contenedor en el 3307 de la PC. Se usa 3307 porque el 3306 ya lo ocupa el MariaDB de la materia IoT, y así conviven los dos |
| `-v pl-datos:/var/lib/mysql` | Guarda los datos en un volumen con nombre, que sobrevive aunque se borre el contenedor |
| `-v "${PWD}\sql:/sql:ro"` | Monta la carpeta `sql` de esta etapa dentro del contenedor, en solo lectura |
| `mariadb:11.4` | La imagen oficial de MariaDB, versión 11.4 (de soporte extendido) |

El montaje de `sql` apunta a la carpeta desde donde se ejecutó el comando. Por eso hay que ejecutarlo desde esta etapa.

## 2. Ejecutar los scripts

Cada script se ejecuta con el cliente `mariadb` que viene dentro del contenedor:

```bash
docker exec pl-mariadb mariadb -u pl -ppl123 --default-character-set=utf8mb4 punto_lacteo -e "source /sql/01_esquema.sql"
```

```bash
docker exec pl-mariadb mariadb -u pl -ppl123 --default-character-set=utf8mb4 punto_lacteo -e "source /sql/02_datos.sql"
```

```bash
docker exec pl-mariadb mariadb -u pl -ppl123 --default-character-set=utf8mb4 --table punto_lacteo -e "source /sql/03_consultas.sql"
```

Las restricciones se prueban con `--force`, para que el cliente siga después de cada error:

```bash
docker exec pl-mariadb mariadb -u pl -ppl123 --default-character-set=utf8mb4 --force punto_lacteo -e "source /sql/04_restricciones.sql"
```

En PowerShell no se puede usar `< archivo.sql` para pasarle un archivo a un comando, y por eso se monta la carpeta y se usa `source`.

## 3. Explorar a mano

Para abrir una consola interactiva de SQL (pide la contraseña, `pl123`):

```bash
docker exec -it pl-mariadb mariadb -u pl -p --default-character-set=utf8mb4 punto_lacteo
```

Algunas órdenes útiles dentro de la consola: `SHOW TABLES;`, `DESCRIBE venta;`, `SHOW CREATE TABLE venta_detalle;` y `exit` para salir.

## 4. Detener y limpiar

| Para… | Comando |
|---|---|
| Detener el contenedor (los datos quedan) | `docker stop pl-mariadb` |
| Volver a arrancarlo | `docker start pl-mariadb` |
| Borrar el contenedor (los datos siguen en el volumen) | `docker rm -f pl-mariadb` |
| Borrar también los datos | `docker volume rm pl-datos` |

El módulo 05 usa este mismo contenedor, así que conviene dejarlo creado.
