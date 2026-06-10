from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.agenda.models.procedimento import Procedimento


class ProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedimento
        fields = ["nome", "valor", "duracao", "ativo"]

    def validate_valor(self, data):
        if data <= 0:
            raise ValidationError("Valor não pode ser igual a zero ou negativo.")

        return data
