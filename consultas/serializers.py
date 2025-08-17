from rest_framework import serializers
from .models import Consulta, Profissional
from django.utils import timezone


class ConsultaSerializer(serializers.ModelSerializer):
    profissional_id = serializers.PrimaryKeyRelatedField(
        queryset=Profissional.objects.all(), source="profissional"
    )

    def validate_paciente_nome(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "O nome do paciente não pode estar vazio."
            )
        return value

    def validate_data_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Não é permitido cadastrar consultas para datas no passado."
            )
        return value

    def validate_observacoes(self, value):
        if value is not None and value.strip() == "":
            raise serializers.ValidationError(
                "Observações, se informadas, não podem estar vazias."
            )
        return value

    class Meta:
        model = Consulta
        fields = ["id", "profissional_id", "paciente_nome", "data_hora", "observacoes"]


class ConsultaDetalheSerializer(serializers.ModelSerializer):
    profissional_id = serializers.IntegerField(source="profissional.id")
    profissional_nome = serializers.CharField(source="profissional.nome_exibicao")
    profissional_especialidade = serializers.CharField(
        source="profissional.especialidade"
    )

    class Meta:
        model = Consulta
        fields = [
            "id",
            "profissional_id",
            "profissional_nome",
            "profissional_especialidade",
            "data_hora",
            "paciente_nome",
            "observacoes",
        ]
