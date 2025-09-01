from django.db import models
from django.core.validators import RegexValidator


class Profissional(models.Model):
    nome = models.CharField(max_length=100, db_index=True)
    nome_social = models.CharField(max_length=100, blank=True, null=True)
    especialidade = models.CharField(max_length=70, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    
    # Validação de telefone brasileiro
    telefone_validator = RegexValidator(
        regex=r'^\(\d{2}\)\d{4,5}-\d{4}$',
        message="Telefone deve estar no formato (11)99999-9999"
    )
    telefone = models.CharField(
        max_length=20, 
        validators=[telefone_validator]
    )
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)  # Soft delete
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['especialidade']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return self.nome_social if self.nome_social else self.nome
