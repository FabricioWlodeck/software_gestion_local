#!/bin/bash
# Se ejecuta una sola vez, cuando MariaDB inicializa un volumen vacío.
# - Crea la base de pruebas del backend y le da permisos al usuario de la aplicación.
# - Crea el usuario del bot con permiso de solo lectura (como 'mediciones' en la materia IoT).
set -euo pipefail

mariadb -u root -p"${MARIADB_ROOT_PASSWORD}" <<SQL
CREATE DATABASE IF NOT EXISTS punto_lacteo_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON punto_lacteo_test.* TO '${MARIADB_USER}'@'%';

CREATE USER IF NOT EXISTS '${TB_DB_USER}'@'%' IDENTIFIED BY '${TB_DB_PASS}';
GRANT SELECT ON \`${MARIADB_DB}\`.* TO '${TB_DB_USER}'@'%';
FLUSH PRIVILEGES;
SQL
