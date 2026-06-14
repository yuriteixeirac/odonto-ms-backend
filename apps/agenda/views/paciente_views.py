from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import OR
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.agenda.models.paciente import Paciente
from apps.agenda.serializers.paciente_serializer import (
    PacienteInputSerializer,
    PacienteOutputSerializer,
)
from apps.common.permissions import IsAppAdmin, IsClinicaAdmin, IsRecepcionista


@extend_schema_view(
    list=extend_schema(
        responses=PacienteOutputSerializer(many=True),
    ),
    retrieve=extend_schema(
        responses=PacienteOutputSerializer,
    ),
    create=extend_schema(
        request=PacienteInputSerializer,
        responses={201: PacienteOutputSerializer, 400: None, 404: None},
    ),
    update=extend_schema(
        request=PacienteInputSerializer,
        responses={200: PacienteOutputSerializer},
    ),
    partial_update=extend_schema(
        request=PacienteInputSerializer,
        responses={200: PacienteOutputSerializer},
    ),
)
class PacienteViewSet(ModelViewSet):
    queryset = Paciente.objects.all()

    permission_classes = [IsAppAdmin | IsRecepcionista | IsClinicaAdmin]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PacienteInputSerializer

        return PacienteOutputSerializer
