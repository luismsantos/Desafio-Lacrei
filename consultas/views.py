from django.shortcuts import render
from rest_framework import viewsets
from .models import Consulta
from .serializers import ConsultaSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    # Filtro para buscar consultas pelo ID do profissional (query param 'profissional_id')
    def get_queryset(self):
        queryset = super().get_queryset()
        profissional_id = self.request.query_params.get('profissional_id')
        if profissional_id:
            queryset = queryset.filter(profissional_id=profissional_id)
        return queryset


