from django.db import models

from apps.agenda.enums import Dia
from config import settings


class Expediente(models.Model):
    dia = models.IntegerField(choices=Dia.choices)
    inicio = models.TimeField()
    fim = models.TimeField()
    ativo = models.BooleanField(default=True)  # type: ignore
    clinico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        unique_together = (
            "ativo",
            "clinico",
            "dia",
        )
