import logging

from django.conf import settings
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint para monitoramento da aplicação
    """
    # Health check simplificado - sempre retorna healthy se Django está rodando
    return JsonResponse(
        {
            "status": "healthy",
            "service": "django",
            "debug": settings.DEBUG,
            "version": "1.0.0",
        }
    )


def readiness_check(request):
    """
    Readiness check simplificado
    """
    return JsonResponse({"status": "ready", "service": "django"})
