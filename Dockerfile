# 1. Usamos Python oficial como base (versión liviana 'slim')
FROM python:3.10-slim

# 2. Variables de entorno para que Python no genere archivos .pyc y los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos dependencias del sistema necesarias para PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# 5. Copiamos los requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto del código
COPY . .

# 7. Exponemos el puerto
EXPOSE 8000

# 8. Comando por defecto para levantar el servidor
CMD ["sh", "-c", "until python src/manage.py migrate --noinput; do echo 'DB no lista, reintentando en 2s...'; sleep 2; done; python src/manage.py collectstatic --noinput; gunicorn core.wsgi:application --chdir src --bind 0.0.0.0:${PORT:-8000}"]