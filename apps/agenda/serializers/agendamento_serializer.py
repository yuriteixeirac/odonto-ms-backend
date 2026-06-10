from datetime import timedelta
from typing import override

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.accounts.serializers.usuario_serializers import UsuarioOutputSerializer
from apps.agenda.models.agendamento import Agendamento
from apps.agenda.serializers.procedimento_serializer import ProcedimentoSerializer


class AgendamentoInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            "inicio",
            "status",
            "observacoes",
            "procedimento",
            "clinico",
        ]

    @override
    def validate(self, attrs):
        if attrs["inicio"] < timezone.now():
            raise ValidationError("Impossível marcar agendamento no passado.")
        return attrs


class AgendamentoOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            "inicio",
            "fim",
            "status",
            "observacoes",
            "procedimento",
            "clinico",
            "criado_em",
        ]
