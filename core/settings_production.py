# Configurações específicas para produção
import os

from .settings import *  # noqa: F403

# Desabilitar debug em produção
DEBUG = False

# ALLOWED_HOSTS para produção - permitir IPs dinâmicos do ECS
ALLOWED_HOSTS = ["*"]  # Para desenvolvimento - em produção usar domínio específico

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Desabilitado - sem SSL
# SECURE_HSTS_PRELOAD = True  # Desabilitado - sem SSL
# SECURE_HSTS_SECONDS = 31536000  # Desabilitado - sem SSL
SECURE_SSL_REDIRECT = False  # Desabilitado - acesso direto HTTP
SESSION_COOKIE_SECURE = False  # Desabilitado - sem SSL
CSRF_COOKIE_SECURE = False  # Desabilitado - sem SSL
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

# Configurações de logging para produção - Console only para ECS
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
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",  # Mais detalhes em produção
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",  # Capturar erros 500
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "consultas": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "profissionais": {
            "handlers": ["console"],
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
