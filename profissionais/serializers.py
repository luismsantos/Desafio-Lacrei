from rest_framework import serializers
from .models import Profissional

class ProfissionalSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.SerializerMethodField()

    class Meta:
        model = Profissional
        fields = ['id', 'nome', 'nome_social', 'nome_exibicao', 'especialidade', 'email', 'telefone']
        
    def get_nome_exibicao(self, obj):
        return obj.nome_social if obj.nome_social else obj.nome

    