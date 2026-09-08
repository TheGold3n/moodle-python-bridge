FROM python:3.10-slim

# Evita que Python escriba archivos .pyc en el disco y asegura que los logs salgan inmediatamente a stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes si hiciera falta
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Puerto expuesto por la API de Django
EXPOSE 8000

# Comando para levantar el servidor de desarrollo en todas las interfaces
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

