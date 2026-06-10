from django.db import models


class Dia(models.IntegerChoices):
    SEGUNDA = 0, "Segunda"  # type: ignore
    TERCA = 1, "Terça"  # type: ignore
    QUARTA = 2, "Quarta"  # type: ignore
    QUINTA = 3, "Quinta"  # type: ignore
    SEXTA = 4, "Sexta"  # type: ignore
    SABADO = 5, "Sábado"  # type: ignore
    DOMINGO = 6, "Domingo"  # type: ignore


class Status(models.TextChoices):
    PENDENTE = "pendente"
    AGENDADO = "agendado"
    CANCELADO = "cancelado"
    CONCLUIDO = "concluído"
