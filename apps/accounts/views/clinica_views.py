from typing import override

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models.clinica import Clinica
from apps.accounts.serializers import ClinicaOutputSerializer
from apps.accounts.serializers.clinica_serializers import ClinicaInputSerializer
from apps.accounts.services import CEPService
from apps.common.helpers import api_response


class ClinicaViewSet(ModelViewSet):
    queryset = Clinica.objects.all()  # type: ignore
    serializer_class = ClinicaOutputSerializer
    permission_classes = [IsAdminUser]

    @override
    def create(self, request, *args, **kwargs):
        serializer = ClinicaInputSerializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Falha ao serializar dados de entrada.",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        cep: str = serializer.validated_data.get("cep")  # type: ignore
        endereco = CEPService.get_endereco(cep)

        clinica = serializer.save(endereco=endereco)

        return api_response(
            success=True,
            status=status.HTTP_201_CREATED,
            data=ClinicaOutputSerializer(clinica).data,  # type: ignore
        )
