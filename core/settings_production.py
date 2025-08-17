# Configurações específicas para produção
import os

from .settings import *  # noqa: F403

# Desabilitar debug em produção
DEBUG = False

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# Configurações de CORS para produção
CORS_ALLOWED_ORIGINS = [
    "https://desafio-lacrei.com",
    "https://www.desafio-lacrei.com",
]

# Configurações de cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

# Configurações de logging para produção
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/django/app.log",
            "maxBytes": 15728640,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "consultas": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "profissionais": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Configurações de email para produção
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@desafio-lacrei.com")

# Configurações de administradores
ADMINS = [
    ("Admin", os.environ.get("ADMIN_EMAIL", "admin@desafio-lacrei.com")),
]

# Configurações de rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"

# Configurações de performance
CONN_MAX_AGE = 60
