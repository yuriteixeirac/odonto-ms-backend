from django.db import models

from apps.accounts.validators import validate_phone
from apps.agenda.validators import validate_cpf


class Paciente(models.Model):
    nome = models.CharField(max_length=128)
    sobrenome = models.CharField(max_length=128)
    cpf = models.CharField(max_length=11, unique=True, validators=[validate_cpf])
    telefone = models.CharField(max_length=13, unique=True, validators=[validate_phone])
    email = models.EmailField(blank=True, null=True)

    clinica = models.ForeignKey("accounts.Clinica", on_delete=models.PROTECT)
