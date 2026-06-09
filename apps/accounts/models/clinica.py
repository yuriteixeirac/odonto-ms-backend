from django.db import models

from apps.accounts.validators import PhoneValidator


class Clinica(models.Model):
    nome = models.CharField(max_length=128, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=13, validators=[PhoneValidator()])
    endereco = models.JSONField(null=True)
