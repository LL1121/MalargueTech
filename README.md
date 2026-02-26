# Malargüe Tech - MVP de Gestión de Reparaciones

Sistema web para un taller técnico de computadoras con arquitectura monolítica modular en Django + PostgreSQL, dockerizado para desarrollo rápido.

## Estado actual del MVP

Incluye:
- Gestión de usuarios con perfil de rol (`Dueño` / `Técnico`).
- Gestión de clientes, equipos y órdenes de reparación.
- Flujo de estados de reparación (`Ingresado`, `En revisión`, `Presupuestado`, `Reparando`, `Reparado`, `Entregado`, `Cancelado`).
- Inventario de repuestos con control de stock.
- Descuento automático de stock al pasar la orden a `Reparado`.
- Registro de movimientos de stock.
- Generación automática de QR por orden.
- Endpoint público por QR para seguimiento del cliente.
- Notificación automática por email al cliente cuando cambia el estado.

## Stack

- Python 3.10
- Django 5.x
- PostgreSQL 16
- Docker + Docker Compose

## Estructura del proyecto

```text
malarguetech/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── docs/
│   └── manual_dueno.md
└── src/
    ├── manage.py
    ├── core/
    ├── usuarios/
    ├── inventario/
    └── taller/
```

## Levantar el entorno

```bash
docker compose up --build -d
```

## Migraciones

```bash
docker compose exec web python src/manage.py makemigrations
docker compose exec web python src/manage.py migrate
```

## Superusuario

```bash
docker compose exec web python src/manage.py createsuperuser
```

## Modo demo (recomendado para presentación)

Carga automáticamente usuarios, clientes, equipos, repuestos y órdenes de ejemplo:

```bash
docker compose exec web python src/manage.py seed_demo
```

Si querés regenerar todo desde cero:

```bash
docker compose exec web python src/manage.py seed_demo --reset
```

Usuarios de demo:
- dueño: `demo_owner` / `Demo1234!`
- técnico: `demo_tecnico1` / `Demo1234!`
- técnico: `demo_tecnico2` / `Demo1234!`

## URLs importantes

- Home API: `http://localhost:8000/`
- Healthcheck app: `http://localhost:8000/health/`
- Admin: `http://localhost:8000/admin/`
- Seguimiento por QR: `http://localhost:8000/seguimiento/<uuid>/`

## Tests

```bash
docker compose exec web python src/manage.py test
```

## Variables de entorno relevantes

En `docker-compose.yml` ya están definidas para desarrollo:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `SITE_BASE_URL`

Para emails reales se recomienda luego configurar SMTP y `EMAIL_BACKEND` en producción.

## Deploy en Railway

Este repo ya está preparado para Railway usando `Dockerfile` + `railway.json`.

### 1) Crear proyecto y conectar repo
- En Railway: **New Project** → **Deploy from GitHub Repo**.

### 2) Agregar PostgreSQL
- En Railway: **New** → **Database** → **PostgreSQL**.

### 3) Configurar variables de entorno del servicio web

Recomendadas:
- `SECRET_KEY` = (valor largo y seguro)
- `DEBUG` = `false`
- `ALLOWED_HOSTS` = `tu-app.up.railway.app`
- `CSRF_TRUSTED_ORIGINS` = `https://tu-app.up.railway.app`
- `DB_NAME` = `${{Postgres.PGDATABASE}}`
- `DB_USER` = `${{Postgres.PGUSER}}`
- `DB_PASSWORD` = `${{Postgres.PGPASSWORD}}`
- `DB_HOST` = `${{Postgres.PGHOST}}`
- `SITE_BASE_URL` = `https://tu-app.up.railway.app`

### 4) Deploy
- Railway ejecuta automáticamente build/deploy.
- El contenedor corre: migraciones, `collectstatic` y `gunicorn`.

### 5) Crear usuario admin en producción

Usar Railway Shell o una ejecución manual:

```bash
python src/manage.py createsuperuser
```

## Manual de uso (Dueño)

Ver: `docs/manual_dueno.md`
