from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Profissional
from .serializers import (
    ProfissionalSerializer,
    ProfissionalListSerializer,
    ProfissionalDetalheSerializer,
)


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """
        Lista e detalhes são públicos, mas criação, edição e exclusão exigem autenticação
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfissionalDetalheSerializer
        elif self.action == "list":
            return ProfissionalListSerializer
        return ProfissionalSerializer
