from django.db import models

from apps.agenda.enums import Status
from config import settings


class Agendamento(models.Model):
    inicio = models.DateTimeField()
    fim = models.DateTimeField()

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDENTE
    )

    observacoes = models.TextField(null=True)

    procedimento = models.ForeignKey("Procedimento", on_delete=models.PROTECT)
    clinico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    paciente = models.ForeignKey("Paciente", on_delete=models.PROTECT)

    criado_em = models.DateTimeField(auto_now_add=True)
