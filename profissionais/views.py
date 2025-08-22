from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.shortcuts import render

from core.throttling import ListingRateThrottle, ProfissionalCreateRateThrottle

from .models import Profissional
from .serializers import (
    ProfissionalDetalheSerializer,
    ProfissionalListSerializer,
    ProfissionalSerializer,
)


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_throttles(self):
        if self.action == "list":
            throttle_classes = [ListingRateThrottle]
        elif self.action in ["create", "update", "partial_update"]:
            throttle_classes = [ProfissionalCreateRateThrottle]
        else:
            throttle_classes = []
        return [throttle() for throttle in throttle_classes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfissionalDetalheSerializer
        elif self.action == "list":
            return ProfissionalListSerializer
        return ProfissionalSerializer
