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

## Manual de uso (Dueño)

Ver: `docs/manual_dueno.md`
