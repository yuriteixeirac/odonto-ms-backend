from typing import override

from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from apps.agenda.models.expediente import Expediente
from apps.agenda.serializers.expediente_serializer import (
    ExpedienteInputSerializer,
    ExpedienteOutputSerializer,
)
from apps.common.helpers import api_response


class ExpedienteViewSet(ModelViewSet):
    queryset = Expediente.objects.all()  # type: ignore
    serializer_class = ExpedienteOutputSerializer

    @override
    def create(self, request, *args, **kwargs):
        serializer = ExpedienteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Falha ao serializar dados de entrada.",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return api_response(
            success=True,
            data=serializer.data,  # type: ignore
            status=status.HTTP_201_CREATED,
        )
