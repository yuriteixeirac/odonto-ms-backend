from rest_framework import serializers

from apps.accounts.enums import Cargo
from apps.accounts.models.usuario import Usuario


class ConviteSerializer(serializers.Serializer):
    cargo = serializers.ChoiceField(choices=Cargo.choices)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["email", "password", "nome", "sobrenome", "telefone"]
