from datetime import datetime, timedelta
from typing import override

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.enums import Cargo
from apps.agenda.enums import Status
from apps.agenda.models.agendamento import Agendamento
from apps.agenda.models.expediente import Expediente
from apps.agenda.serializers import AgendamentoInputSerializer
from apps.agenda.serializers.agendamento_serializer import AgendamentoOutputSerializer
from apps.common import publisher
from apps.common.helpers import api_response
from apps.common.permissions import IsRecepcionista


class AgendamentoViewSet(ModelViewSet):
    serializer_class = AgendamentoInputSerializer
    queryset = Agendamento.objects.all()  # type: ignore

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsRecepcionista]

    @override
    def create(self, request, *args, **kwargs):
        serializer = AgendamentoInputSerializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Falha ao serializar dados de entrada.",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clínico tem que existir
        clinico = serializer.validated_data["clinico"]  # type: ignore

        if clinico.cargo != Cargo.CLINICO:
            return api_response(
                success=False,
                message="Falha ao realizar operação.",
                errors={"erro": "Clínico não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        procedimento = serializer.validated_data["procedimento"]  # type: ignore

        if not procedimento.ativo:
            return api_response(
                success=False,
                errors={"erro": "Nenhum procedimento ativo encontrado."},
                message="Falha ao realizar operação",
                status=status.HTTP_404_NOT_FOUND,
            )

        # Agendamento tem que estar dentro do expediente do clínico selecionado
        inicio: datetime = serializer.validated_data["inicio"]  # type: ignore
        fim: datetime = inicio + timedelta(minutes=procedimento.duracao)  # type: ignore

        dia = inicio.weekday()

        expediente_valido = Expediente.objects.filter(dia=dia, clinico=clinico).first()  # type: ignore

        if not expediente_valido:
            return api_response(
                success=False,
                message="Falha ao realizar operação.",
                errors={"erro": "Clínico não tem expediente para esse dia da semana."},
                status=status.HTTP_404_NOT_FOUND,
            )

        agendamento_overlap = (
            Agendamento.objects.filter(clinico=clinico, inicio__lt=fim, fim__gt=inicio)  # type: ignore
            .exclude(status=Status.CANCELADO)
            .exists()
        )

        if agendamento_overlap:
            return api_response(
                success=False,
                message="Falha ao realizar operação",
                errors={
                    "erro": "Já existe agendamento para esse clínico nesse intervalo de tempo."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expediente_overlap = (
            Expediente.objects.filter(  # type: ignore
                dia=dia, inicio__lte=inicio.time(), fim__gt=fim.time(), clinico=clinico
            )
            .exclude(ativo=False)
            .exists()
        )

        if expediente_overlap:
            return api_response(
                success=False,
                message="Falha ao realizar operação",
                errors={
                    "erro": "Duração do agendamento não está dentro do expediente do clínico."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        agendamento = Agendamento(
            **serializer.validated_data,  # type: ignore
            fim=fim,
        )
        agendamento.save()

        publisher.publish_lembrete(agendamento_id=agendamento.id)  # type: ignore

        return api_response(
            success=True,
            status=status.HTTP_201_CREATED,
            data=AgendamentoOutputSerializer(agendamento).data,  # type: ignore
        )
