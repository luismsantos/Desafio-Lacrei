from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfissionalViewSet

router = DefaultRouter()
router.register(r"profissionais", ProfissionalViewSet, basename="profissional")

urlpatterns = [
    path("", include(router.urls)),
]
