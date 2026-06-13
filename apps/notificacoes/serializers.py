from rest_framework import serializers

from apps.accounts.validators import validate_phone
from apps.notificacoes.models import WhatsAppInstance


class WhatsAppInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppInstance
        fields = "__all__"


class MensagemSerializer(serializers.Serializer):
    mensagem = serializers.CharField()
    telefone = serializers.CharField(validators=[validate_phone])
