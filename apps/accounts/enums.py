from django.db import models


class Cargo(models.TextChoices):
    ADMIN = "administrador"
    RECEPCAO = "recepção"
    CLINICO = "clínico"
    AUXILIAR = "auxiliar"
