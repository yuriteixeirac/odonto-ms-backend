from django.db import models


class Cargo(models.TextChoices):
    ADMIN = "administrador"
    RECEPCIONISTA = "recepcionista"
    CLINICO = "clínico"
    AUXILIAR = "auxiliar"
