import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

def env_str(name, default=""):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip()


SECRET_KEY = env_str("SECRET_KEY", "django-insecure-dev-only-change-me") or "django-insecure-dev-only-change-me"


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}

DEBUG = env_bool("DEBUG", default=True)

def normalize_host(value):
    host = value.strip()
    if not host:
        return ""
    if "://" in host:
        parsed = urlparse(host)
        return (parsed.hostname or "").strip()
    host = host.split("/")[0]
    return host.split(":")[0].strip()


raw_allowed_hosts = env_str("ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [normalize_host(host) for host in raw_allowed_hosts.split(",") if normalize_host(host)] or ["*"]

def normalize_origin(value):
    origin = value.strip()
    if not origin:
        return ""
    if "://" not in origin:
        origin = f"https://{origin}"
    parsed = urlparse(origin)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


raw_csrf_origins = env_str("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    normalize_origin(origin)
    for origin in raw_csrf_origins.split(",")
    if normalize_origin(origin)
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "usuarios.apps.UsuariosConfig",
    "inventario.apps.InventarioConfig",
    "taller.apps.TallerConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DB_NAME = env_str("DB_NAME") or env_str("PGDATABASE")
DB_USER = env_str("DB_USER") or env_str("PGUSER")
DB_PASSWORD = env_str("DB_PASSWORD") or env_str("PGPASSWORD")
DB_HOST = env_str("DB_HOST") or env_str("PGHOST")
DB_PORT = env_str("DB_PORT") or env_str("PGPORT") or "5432"
DATABASE_URL = env_str("DATABASE_URL")
if DATABASE_URL and "://" not in DATABASE_URL:
    DATABASE_URL = ""
DB_SSL_REQUIRE = env_bool("DB_SSL_REQUIRE", default=False)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=DB_SSL_REQUIRE,
        )
    }
elif all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "OPTIONS": {"sslmode": "require"} if DB_SSL_REQUIRE else {},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@malarguetech.local")
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://localhost:8000")

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"