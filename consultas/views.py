from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.shortcuts import render

from .models import Consulta
from .serializers import ConsultaDetalheSerializer, ConsultaSerializer


class ListingRateThrottle(AnonRateThrottle):
    scope = 'listing'


class ConsultaCreateRateThrottle(UserRateThrottle):
    scope = 'consulta_create'


class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_throttles(self):
        if self.action == 'list':
            throttle_classes = [ListingRateThrottle]
        elif self.action in ['create', 'update', 'partial_update']:
            throttle_classes = [ConsultaCreateRateThrottle]
        else:
            throttle_classes = []
        return [throttle() for throttle in throttle_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        profissional_id = self.request.query_params.get("profissional_id")
        if profissional_id:
            queryset = queryset.filter(profissional_id=profissional_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.query_params.get("profissional_id") and not queryset.exists():
            raise NotFound(
                detail="Nenhuma consulta encontrada para o profissional informado."
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConsultaDetalheSerializer
        return ConsultaSerializer
