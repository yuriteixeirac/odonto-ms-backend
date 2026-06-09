from django.db import models

from apps.agenda.enums import Dia, Status
from config import settings


class Expediente(models.Model):
    dia = models.IntegerChoices(choices=Dia.choices)
    inicio = models.TimeField()
    fim = models.TimeField()
    ativo = models.BooleanField(default=True)  # type: ignore

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDENTE
    )

    procedimento = models.ForeignKey("Procedimento", on_delete=models.PROTECT)
    clinico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("clinico", "dia", "ativo")
