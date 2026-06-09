from typing import override

from rest_framework import serializers

from apps.accounts.models.usuario import Usuario
from apps.accounts.validators import validate_phone


class UsuarioInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["email", "password", "nome", "sobrenome"]

    telefone = serializers.CharField(max_length=13, validators=[validate_phone])

    @override
    def save(self, **kwargs):
        return Usuario.objects.create_user(**self.validated_data, **kwargs)  # type: ignore


class UsuarioOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["email", "nome", "sobrenome", "telefone"]
