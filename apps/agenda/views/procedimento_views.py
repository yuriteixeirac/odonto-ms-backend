from typing import override

from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from apps.agenda.models.procedimento import Procedimento
from apps.agenda.serializers.procedimento_serializer import ProcedimentoSerializer
from apps.common.helpers import api_response


class ProcedimentoViewSet(ModelViewSet):
    serializer_class = ProcedimentoSerializer
    queryset = Procedimento.objects.all()  # type: ignore

    @override
    def create(self, request, *args, **kwargs):
        serializer = ProcedimentoSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Falha ao serializar dados de entrada.",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        procedimento = Procedimento(**serializer.validated_data)  # type: ignore
        procedimento.clinica = request.user.clinica

        return api_response(
            success=True,
            status=status.HTTP_201_CREATED,
            data=serializer.data,  # type: ignore
        )
