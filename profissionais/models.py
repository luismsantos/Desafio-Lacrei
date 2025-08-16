from django.db import models

# Create your models here.

class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    nome_social = models.CharField(max_length=100, blank=True, null=True)
    especialidade = models.CharField(max_length=70)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome