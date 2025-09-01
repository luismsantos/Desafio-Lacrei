from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from profissionais.models import Profissional

# Create your models here.

class Consulta(models.Model):
    profissional = models.ForeignKey(
        Profissional, 
        related_name="consultas", 
        on_delete=models.CASCADE,
        db_index=True  
    )
    paciente_nome = models.CharField(max_length=100, db_index=True)
    data_hora = models.DateTimeField(db_index=True)  
    observacoes = models.TextField(blank=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        constraints = [
            models.UniqueConstraint(
                fields=['profissional', 'data_hora'],
                name='unique_consulta_profissional_horario'
            )
        ]
        indexes = [
            models.Index(fields=['profissional', 'data_hora']),
            models.Index(fields=['data_hora']),
        ]
    
    def clean(self):
        if self.data_hora and self.data_hora < timezone.now():
            raise ValidationError("Não é possível agendar consultas no passado.")

    def __str__(self):
        return f"{self.paciente_nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
