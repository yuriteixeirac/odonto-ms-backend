from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models.usuario import Usuario
from apps.accounts.serializers import UsuarioOutputSerializer
from apps.common.helpers import api_response
from apps.common.permissions import (
    IsAppAdmin,
    IsClinicaAdmin,
    IsClinico,
    IsRecepcionista,
)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAppAdmin | IsClinicaAdmin | IsRecepcionista | IsClinico])
def me_view(request):
    return api_response(success=True, data=UsuarioOutputSerializer(request.user).data)


class UsuarioViewSet(ReadOnlyModelViewSet):
    serializer_class = UsuarioOutputSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAppAdmin | IsClinicaAdmin | IsRecepcionista | IsClinico]

    def get_queryset(self):
        user = self.request.user
        queryset = Usuario.objects.all()

        cargo = self.request.query_params.get("cargo")
        if cargo:
            queryset = queryset.filter(cargo=cargo)

        if getattr(user, "clinica_id", None) is None and getattr(user, "is_staff", False):
            return queryset

        if user.cargo == "clínico":
            return queryset.filter(pk=user.pk)

        return queryset.filter(clinica_id=user.clinica_id)
