from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import ConsultaViewSet

router = DefaultRouter()
router.register(r"consultas", ConsultaViewSet, basename="consulta")

urlpatterns = [
    path("", include(router.urls)),
]
