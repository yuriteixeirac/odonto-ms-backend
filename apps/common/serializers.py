from rest_framework import serializers


class ApiResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(allow_blank=True, required=False)
    data = serializers.JSONField(required=False, allow_null=True)  # type: ignore
    errors = serializers.JSONField(required=False, allow_null=True)  # type: ignore
    meta = serializers.JSONField(required=False)
