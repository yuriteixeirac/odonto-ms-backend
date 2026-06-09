from rest_framework import serializers

from apps.accounts.enums import Cargo


class ConviteSerializer(serializers.Serializer):
    cargo = serializers.ChoiceField(choices=Cargo.choices)
