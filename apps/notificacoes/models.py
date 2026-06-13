from django.db import models


class WhatsAppInstance(models.Model):
    instancia_id = models.CharField(max_length=256)
    nome = models.CharField(max_length=256, unique=True)
    clinica = models.OneToOneField("accounts.Clinica", on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)  # type: ignore

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
