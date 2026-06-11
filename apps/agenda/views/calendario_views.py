from calendar import monthrange
from datetime import date, datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.helpers import api_response
from apps.agenda.enums import Status
from apps.agenda.models.agendamento import Agendamento
from apps.agenda.serializers.calendario_mensal_serializer import (
    CalendarioMensalSerializer,
)
from apps.common.permissions import IsClinico


@api_view(["GET"])
@permission_classes([IsClinico])
@authentication_classes([JWTAuthentication])
def calendario_mensal_view(request):
    ano_param = request.query_params.get("ano")
    mes_param = request.query_params.get("mes")

    if not (ano_param and mes_param):
        return api_response(
            success=False,
            message="Falha ao associar valores de entrada.",
            errors={"erro": "Ano e mês são parâmetros necessários."},
            status=400,
        )

    try:
        ano = int(ano_param)
        mes = int(mes_param)
    except ValueError:
        return api_response(
            success=False,
            message="Falha ao associar valores de entrada.",
            errors={"erro": "Ano ou mês inválidos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if mes not in list(range(1, 12 + 1)):
        return api_response(
            success=False,
            message="Falha ao serializar dados de entrada.",
            errors={"erro": f"Mês {mes} deve estar entre 1 e 12."},
            status=400,
        )

    inicio_mes = timezone.make_aware(datetime(ano, mes, 1))
    fim_mes = (
        timezone.make_aware(datetime(ano + 1, 1, 1))
        if mes == 12
        else timezone.make_aware(datetime(ano, mes + 1, 1))
    )

    agendamentos = Agendamento.objects.filter(
        inicio__gte=inicio_mes, inicio__lt=fim_mes, clinico=request.user
    )

    datas = []
    for dia in range(1, monthrange(ano, mes)[1] + 1):
        inicio_dia = timezone.make_aware(datetime(ano, mes, dia))
        fim_dia = inicio_dia + timezone.timedelta(days=1)

        agendamentos_dia = agendamentos.filter(
            inicio__gte=inicio_dia,
            inicio__lt=fim_dia,
        )

        contagem_por_status = {}

        for agendamento_status in Status.values:
            contagem_por_status[agendamento_status] = agendamentos_dia.filter(
                status=agendamento_status
            ).count()

        datas.append(
            {
                "data": date(year=ano, month=mes, day=dia),
                "total": agendamentos_dia.count(),
                "contagem_por_status": contagem_por_status,
            }
        )

    serializer = CalendarioMensalSerializer(
        data={"ano": ano, "mes": mes, "dias": datas}
    )

    if not serializer.is_valid():
        return api_response(
            success=False,
            message="Falha ao serializar dados internos.",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=serializer.errors,
        )

    return api_response(success=True, data=serializer.data, status=status.HTTP_200_OK)  # type: ignore
