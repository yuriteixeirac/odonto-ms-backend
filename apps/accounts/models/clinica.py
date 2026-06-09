from django.db import models

from apps.accounts.validators import validate_phone


class Clinica(models.Model):
    nome = models.CharField(max_length=128, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=13, validators=[validate_phone])
    endereco = models.JSONField(null=True)
