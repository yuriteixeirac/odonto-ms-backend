import json
from uuid import uuid4

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.serializers import (
    ConviteSerializer,
    UsuarioInputSerializer,
    UsuarioOutputSerializer,
)
from apps.common.helpers import api_response
from apps.common.permissions import IsClinicaAdmin
from apps.common.redis import redis_cli

CONVITE_TTL_SECONDS = 60 * 60 * 12  # 12 horas


@api_view(["POST"])
@permission_classes([IsClinicaAdmin])
@authentication_classes([JWTAuthentication])
def criar_convite_view(request):
    serializer = ConviteSerializer(data=request.data)

    if not serializer.is_valid():
        return api_response(
            success=False,
            status=status.HTTP_400_BAD_REQUEST,
            message="Não foi possível interpretar os dados recebidos.",
            errors=serializer.errors,
        )

    convite_uuid = str(uuid4())
    clinica_id = request.user.clinica.id

    criado = redis_cli.set(
        f"convite:{convite_uuid}",
        json.dumps(
            {"clinica_id": clinica_id, "cargo": serializer.validated_data["cargo"]}  # type: ignore
        ),
        ex=CONVITE_TTL_SECONDS,
        nx=True,
    )

    if not criado:
        return api_response(
            success=False,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Não foi possível criar o convite.",
            errors={"erro": "Tente novamente."},
        )

    return api_response(
        success=True,
        status=status.HTTP_201_CREATED,
        data={"convite": convite_uuid, "expires_in": CONVITE_TTL_SECONDS},
    )


@api_view(["POST"])
def usar_convite_view(request, convite_uuid: str):
    key = f"convite:{convite_uuid}"
    convite = redis_cli.get(key)

    if not convite:
        return api_response(
            success=False,
            message="Falha ao consultar convite.",
            errors={"erro": "Convite expirou ou não existe"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UsuarioInputSerializer(data=request.data)

    if not serializer.is_valid():
        return api_response(
            success=False,
            message="Falha ao serializar dados de entrada.",
            errors=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    convite_data = json.loads(convite)  # type: ignore
    usuario = serializer.save(
        cargo=convite_data.get("cargo"), clinica_id=convite_data.get("clinica_id")
    )

    redis_cli.delete(key)

    return api_response(
        success=True,
        status=status.HTTP_201_CREATED,
        data=UsuarioOutputSerializer(usuario).data,  # type: ignore
    )
