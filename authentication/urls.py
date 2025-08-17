from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('registrar/', views.registrar, name='auth-registrar'),
    path('entrar/', views.entrar, name='auth-entrar'),
    path('sair/', views.sair, name='auth-sair'),
    path('perfil/', views.perfil, name='auth-perfil'),
    path('token/atualizar/', TokenRefreshView.as_view(), name='token-atualizar'),
]
