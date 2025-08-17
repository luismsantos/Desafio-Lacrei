from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Profissional
import re


class ProfissionalSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.SerializerMethodField()
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Profissional.objects.all())]
    )

    class Meta:
        model = Profissional
        fields = ['id', 'nome', 'nome_social', 'nome_exibicao', 'especialidade', 'email', 'telefone']

    def get_nome_exibicao(self, obj):
        return obj.nome_social if obj.nome_social else obj.nome

    def validate_nome(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("O nome não pode estar vazio.")
        return value

    def validate_especialidade(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Especialidade não pode estar vazia.")
        return value

    def validate_telefone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Telefone não pode estar vazio.")
        if not re.match(r'^[0-9\-\+\(\) ]+$', value):
            raise serializers.ValidationError("Telefone contém caracteres inválidos.")
        if len(value) < 8:
            raise serializers.ValidationError("Telefone muito curto.")
        return value

    def validate_nome_social(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("Nome social, se informado, não pode ser vazio.")
        return value


class ProfissionalListSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.SerializerMethodField()

    class Meta:
        model = Profissional
        fields = ['id', 'nome_exibicao', 'especialidade', 'email', 'telefone']

    def get_nome_exibicao(self, obj):
        return obj.nome_social if obj.nome_social else obj.nome


class ProfissionalDetalheSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.SerializerMethodField()

    class Meta:
        model = Profissional
        fields = ['id', 'nome', 'nome_social', 'nome_exibicao', 'especialidade', 'email', 'telefone']

    def get_nome_exibicao(self, obj):
        return obj.nome_social if obj.nome_social else obj.nome
