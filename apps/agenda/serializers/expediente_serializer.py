from typing import override

from django.test.testcases import ValidationError
from rest_framework import serializers

from apps.accounts.serializers.usuario_serializers import UsuarioOutputSerializer
from apps.agenda.enums import Dia
from apps.agenda.models.expediente import Expediente


class ExpedienteInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expediente
        fields = ["id", "inicio", "fim", "ativo", "dia", "clinico"]

    @override
    def validate(self, attrs):
        inicio = attrs.get("inicio")
        fim = attrs.get("fim")

        if inicio >= fim:
            raise ValidationError(
                "O início de um expediente não pode ser posterior ou igual ao seu fim."
            )

        return attrs


class ExpedienteOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expediente
        fields = ["inicio", "fim", "ativo", "dia", "clinico"]

    dia = serializers.SerializerMethodField()
    clinico = UsuarioOutputSerializer()

    def get_dia(self, instance):
        return Dia(instance.dia).label
