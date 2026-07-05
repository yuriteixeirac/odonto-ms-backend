from typing import override

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.agenda.models.procedimento import Procedimento
from apps.agenda.serializers.procedimento_serializer import ProcedimentoSerializer
from apps.common.helpers import api_response
from apps.common.permissions import IsClinicaAdmin, IsClinico, IsRecepcionista


class ProcedimentoViewSet(ModelViewSet):
    serializer_class = ProcedimentoSerializer
    queryset = Procedimento.objects.all()  # type: ignore

    permission_classes = [IsClinicaAdmin | IsClinico | IsRecepcionista]
    authentication_classes = [JWTAuthentication]

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
        procedimento.save()

        return api_response(
            success=True,
            status=status.HTTP_201_CREATED,
            data=ProcedimentoSerializer(procedimento).data,  # type: ignore
        )

    def get_queryset(self):
        user = self.request.user

        if getattr(user, "clinica_id", None):
            return Procedimento.objects.filter(clinica_id=user.clinica_id)  # type: ignore

        return Procedimento.objects.all()  # type: ignore
