from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.common.helpers import api_response
from apps.common.permissions import IsRecepcionistaOuAdmin
from apps.notificacoes.exceptions import (
    InstanciaWhatsAppJaExiste,
    InstanciaWhatsAppNaoEncontrada,
)
from apps.notificacoes.models import WhatsAppInstance
from apps.notificacoes.serializers import MensagemSerializer, WhatsAppInstanceSerializer
from apps.notificacoes.service import WhatsappService


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsRecepcionistaOuAdmin])
def criar_instancia(request):
    clinica = getattr(request.user, "clinica", None)

    if not clinica:
        return api_response(
            success=False,
            message="Falha ao realizar operação.",
            errors={
                "erro": "Usuário não está associado a uma clínica. Provavelmente administrador de aplicação."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    wpp_service = WhatsappService()

    try:
        instancia = wpp_service.criar_instancia(clinica)
    except InstanciaWhatsAppJaExiste:
        return api_response(
            success=False,
            message="Falha ao realizar operação.",
            errors={"erro": "Instância de WhatsApp associada à clínica já existe."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = WhatsAppInstanceSerializer(instancia)

    return api_response(success=True, data=serializer.data, status=status.HTTP_200_OK)  # type: ignore


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsRecepcionistaOuAdmin])
def conectar_instancia(request):
    clinica = getattr(request.user, "clinica", None)

    if not clinica:
        return api_response(
            success=False,
            message="Falha ao realizar operação.",
            errors={
                "erro": "Usuário não está associado a uma clínica. Provavelmente administrador de aplicação."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    wpp_service = WhatsappService()
    instance = WhatsAppInstance.objects.filter(clinica=clinica).first()  # type: ignore

    if not instance:
        return api_response(
            success=False,
            message="Falha ao realizar operação.",
            errors={"erro": "Clínica não possui instância associada."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        qr_code = wpp_service.get_conexao(instance)
    except InstanciaWhatsAppNaoEncontrada:
        return api_response(
            success=False,
            errors={
                "erro": "Instância de WhatsApp associada a clínica ainda não existe."
            },
            message="Falha ao realizar operação.",
            status=status.HTTP_404_NOT_FOUND,
        )

    return api_response(
        success=True, data={"qr_code": qr_code}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsRecepcionistaOuAdmin])
def enviar_mensagem(request):
    clinica = getattr(request.user, "clinica", None)

    if not clinica:
        return api_response(
            success=False,
            message="Falha ao realizar operação.",
            errors={
                "erro": "Usuário não está associado a uma clínica. Provavelmente administrador de aplicação."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = MensagemSerializer(data=request.data)

    if not serializer.is_valid():
        return api_response(
            success=False,
            message="Falha ao realizar operação",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors,
        )

    instance = WhatsAppInstance.objects.filter(clinica=clinica).first()  # type: ignore

    wpp_service = WhatsappService()
    wpp_service.enviar_mensagem(
        instance,
        telefone=serializer.validated_data["telefone"],  # type: ignore
        mensagem=serializer.validated_data["mensagem"],  # type: ignore
    )

    return api_response(success=True, status=status.HTTP_200_OK)
