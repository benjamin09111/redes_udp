# Imagen única para el ETL, los cargadores, el ruteo y el servidor web.
# Versión fijada para que todos los pasos corran con las mismas librerías.
FROM python:3.12.15-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
