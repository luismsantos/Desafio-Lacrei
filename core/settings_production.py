# Configurações específicas para produção
import os

from .settings import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
X_FRAME_OPTIONS = "DENY"

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://desafio-lacrei.com",
    "https://www.desafio-lacrei.com",
]

# Cache em memória
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "production-cache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 3,
        },
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
            "formatter": "verbose",
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
            "level": "ERROR",
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

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@desafio-lacrei.com")

ADMINS = [
    ("Admin", os.environ.get("ADMIN_EMAIL", "admin@desafio-lacrei.com")),
]

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"

CONN_MAX_AGE = 60

# Django REST Framework para produção
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "300/hour",
        "user": "1000/hour", 
        "login": "10/hour",
        "registration": "5/hour",
        "listing": "500/hour",
        "consulta_create": "50/hour",
        "profissional_create": "10/hour",
        "sensitive_data": "100/hour",
    },
}
