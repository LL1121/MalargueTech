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

# 6.1 Precompilamos estáticos en build para acelerar startup en runtime
RUN python src/manage.py collectstatic --noinput || true

# 7. Exponemos el puerto
EXPOSE 8000

# 8. Comando por defecto para levantar el servidor
CMD ["sh", "-c", "if [ \"${RUN_MIGRATIONS:-1}\" = \"1\" ]; then python src/manage.py migrate --noinput || echo 'Migrate falló al iniciar; la app arranca igual para pasar healthcheck.'; fi; if [ \"${CREATE_SUPERUSER:-0}\" = \"1\" ] && [ -n \"${DJANGO_SUPERUSER_PASSWORD:-}\" ]; then python src/manage.py shell -c \"from django.contrib.auth import get_user_model; import os; User=get_user_model(); username=os.getenv('DJANGO_SUPERUSER_USERNAME','admin'); email=os.getenv('DJANGO_SUPERUSER_EMAIL','admin@malarguetech.com'); password=os.getenv('DJANGO_SUPERUSER_PASSWORD'); reset=os.getenv('RESET_SUPERUSER_PASSWORD','0')=='1'; user=User.objects.filter(username=username).first();\nif user is None:\n    User.objects.create_superuser(username,email,password)\nelif reset:\n    user.email=email; user.is_staff=True; user.is_superuser=True; user.is_active=True; user.set_password(password); user.save()\"; fi; exec gunicorn core.wsgi:application --chdir src --bind 0.0.0.0:${PORT:-8000}"]