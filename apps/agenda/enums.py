from django.db import models


class Dia(models.IntegerChoices):
    DOMINGO = 0
    SEGUNDA = 1
    TERCA = 2
    QUARTA = 3
    QUINTA = 4
    SEXTA = 5
    SABADO = 6


class Status(models.TextChoices):
    PENDENTE = "pendente"
    AGENDADO = "agendado"
    CANCELADO = "cancelado"
    CONCLUIDO = "concluído"
