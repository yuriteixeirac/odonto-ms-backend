from django.db import models


class Agendamento(models.Model):
    nome = models.CharField(max_length=255)
    duracao = models.IntegerField()  # em minutos
    valor = models.DecimalField()
    ativo = models.BooleanField(default=True)  # type: ignore

    clinica = models.ForeignKey("Clinica", on_delete=models.CASCADE)
