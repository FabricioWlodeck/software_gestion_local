# Imagen del backend. Compose la construye con la carpeta 06_seguridad como contexto.
FROM python:3.12-slim

# No escribir archivos .pyc y mostrar los mensajes al instante en los registros de Docker.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero solo las dependencias: Docker reutiliza esta capa mientras requirements.txt no cambie.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después el código, que cambia seguido.
COPY . .

EXPOSE 8000

# Al arrancar: aplica las migraciones, carga los datos iniciales y levanta el servidor.
CMD ["sh", "-c", "alembic upgrade head && python -m app.semilla && fastapi run app/main.py --host 0.0.0.0 --port 8000"]
