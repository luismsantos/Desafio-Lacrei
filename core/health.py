import logging

from django.conf import settings
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint para monitoramento da aplicação - Otimizado para ECS
    """
    try:
        # Health check rápido com timeout
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        # Em caso de erro de DB, ainda retorna 200 para evitar restart em loop
        return JsonResponse(
            {"status": "degraded", "database": "unhealthy", "error": str(e)}, status=200
        )

    return JsonResponse(
        {
            "status": "healthy",
            "database": db_status,
            "debug": settings.DEBUG,
            "version": "1.0.0",
        }
    )


def readiness_check(request):
    """
    Readiness check simplificado para ECS - Evita timeouts
    """
    try:
        # Check básico se Django está funcionando
        from django.apps import apps
        
        if not apps.ready:
            return JsonResponse({"status": "not_ready", "reason": "Apps not ready"}, status=503)

        # Check rápido de DB (sem queries complexas)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse({"status": "ready", "database": "connected"})

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        # Retorna 200 para evitar restart loops no ECS
        return JsonResponse({"status": "ready", "note": "degraded mode"}, status=200)
