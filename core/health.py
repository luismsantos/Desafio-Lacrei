from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint para monitoramento da aplicação
    """
    try:
        # Verificar conexão com banco de dados
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        return JsonResponse({
            "status": "unhealthy",
            "database": db_status,
            "error": str(e)
        }, status=503)
    
    return JsonResponse({
        "status": "healthy",
        "database": db_status,
        "debug": settings.DEBUG,
        "version": "1.0.0"
    })

def readiness_check(request):
    """
    Readiness check para Kubernetes/ECS
    """
    try:
        # Verificações mais abrangentes
        from django.core.management import execute_from_command_line
        from django.apps import apps
        
        # Verificar se todas as apps estão carregadas
        if not apps.ready:
            return JsonResponse({
                "status": "not_ready",
                "reason": "Apps not ready"
            }, status=503)
        
        # Verificar conexão com banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            
        return JsonResponse({
            "status": "ready",
            "database": "connected"
        })
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            "status": "not_ready",
            "error": str(e)
        }, status=503)
