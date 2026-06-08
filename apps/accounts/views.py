import json
from uuid import uuid4

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.helpers import api_response
from apps.accounts.permissions import IsClinicAdmin
from apps.accounts.serializers import ConviteSerializer
from apps.common.redis import redis_cli

CONVITE_TTL_SECONDS = 60 * 60 * 12  # 12 horas


@api_view(["POST"])
@permission_classes([IsClinicAdmin])
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


# @api_view(["POST"])
# def usar_convite_view(request, convite_uuid: str):
#     convite = redis_cli.get(f"convite:{convite_uuid}")
