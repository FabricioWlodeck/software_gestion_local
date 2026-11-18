FROM python:3.12-slim

ENV TZ=America/Argentina/Buenos_Aires \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero las dependencias: esta capa se reutiliza mientras requirements.txt no cambie.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Al arrancar: aplica las migraciones, carga la semilla (solo si la base está vacía) y levanta la API.
CMD ["sh", "-c", "alembic upgrade head && python -m app.semilla && fastapi run app/main.py --host 0.0.0.0 --port 8000"]
