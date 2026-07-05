from typing import override

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.agenda.models.expediente import Expediente
from apps.agenda.serializers.expediente_serializer import (
    ExpedienteInputSerializer,
    ExpedienteOutputSerializer,
)
from apps.common.helpers import api_response
from apps.common.permissions import IsClinicaAdmin, IsRecepcionista


class ExpedienteViewSet(ModelViewSet):
    queryset = Expediente.objects.all()  # type: ignore
    serializer_class = ExpedienteOutputSerializer

    permission_classes = [IsClinicaAdmin | IsRecepcionista]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user

        if getattr(user, "clinica_id", None):
            return Expediente.objects.filter(clinico__clinica_id=user.clinica_id)  # type: ignore

        return Expediente.objects.all()  # type: ignore

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
