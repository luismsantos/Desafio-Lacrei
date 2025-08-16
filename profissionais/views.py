from django.shortcuts import render
from rest_framework import viewsets
from .models import Profissional
from .serializers import ProfissionalSerializer

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']