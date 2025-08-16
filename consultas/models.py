from django.db import models
from profissionais.models import Profissional

# Create your models here.

class Consulta(models.Model):
    profissional = models.ForeignKey(Profissional, related_name='consultas', on_delete=models.CASCADE)
    paciente_nome = models.CharField(max_length=100)
    data_hora = models.DateTimeField()
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.paciente_nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
