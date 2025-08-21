"""
Views de debug para diagnóstico de problemas na aplicação.
"""
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.core.cache import cache
import os


class HealthCheckView(View):
    """
    View para verificação de saúde da aplicação.
    """

    def get(self, request):
        """
        Endpoint de health check com informações de debug.
        """
        try:
            # Teste de conexão com cache
            cache_status = "OK"
            try:
                cache.set("test_key", "test_value", 10)
                cached_value = cache.get("test_key")
                if cached_value != "test_value":
                    cache_status = "FAILED - Value mismatch"
            except Exception as e:
                cache_status = f"FAILED - {str(e)}"

            # Verificar configurações Redis
            redis_config = None
            if hasattr(settings, "CACHES"):
                redis_config = settings.CACHES.get("default", {})

            response_data = {
                "status": "OK",
                "debug": settings.DEBUG,
                "environment": {
                    "DATABASE_URL_SET": bool(os.getenv("DATABASE_URL")),
                    "SECRET_KEY_SET": bool(os.getenv("SECRET_KEY")),
                    "REDIS_URL_SET": bool(os.getenv("REDIS_URL")),
                },
                "cache": {
                    "status": cache_status,
                    "backend": redis_config.get("BACKEND") if redis_config else "Not configured",
                    "location": redis_config.get("LOCATION") if redis_config else "Not configured",
                },
                "apps": [app for app in settings.INSTALLED_APPS if not app.startswith("django")],
            }

            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "ERROR",
                "error": str(e),
                "debug": settings.DEBUG,
            }, status=500)


class CacheTestView(View):
    """
    View para testar funcionalidade de cache.
    """

    def get(self, request):
        """
        Testa operações de cache.
        """
        try:
            import redis as redis_lib
            redis_available = True
        except ImportError:
            redis_available = False

        try:
            # Testes básicos de cache
            cache.set("debug_test", "cache_working", 30)
            cached_value = cache.get("debug_test")
            cache.delete("debug_test")

            return JsonResponse({
                "cache_test": "SUCCESS",
                "cached_value": cached_value,
                "redis_library_available": redis_available,
                "cache_backend": str(cache),
            })

        except Exception as e:
            return JsonResponse({
                "cache_test": "FAILED",
                "error": str(e),
                "redis_library_available": redis_available,
            }, status=500)