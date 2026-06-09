from django.db import models


class Procedimento(models.Model):
    nome = models.CharField(max_length=255)
    duracao = models.IntegerField()  # em minutos
    valor = models.DecimalField()
    ativo = models.BooleanField(default=True)  # type: ignore

    clinica = models.ForeignKey("Clinica", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracao__gte=1), name="duracao_gte_1"
            ),
            models.CheckConstraint(
                condition=models.Q(valor__gte=1), name="valor_gte_1"
            ),
        ]

        unique_together = (
            "nome",
            "clinica",
        )
