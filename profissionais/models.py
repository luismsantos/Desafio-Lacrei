from django.db import models

class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    nome_social = models.CharField(max_length=100, blank=True, null=True)
    especialidade = models.CharField(max_length=70)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

    @property
    def nome_exibicao(self):
        return self.nome_social if self.nome_social else self.nome
