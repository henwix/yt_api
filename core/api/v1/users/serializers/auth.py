from rest_framework import serializers

from core.api.v1.common.serializers.serializers import CaptchaSerializer


class AuthInSerializer(CaptchaSerializer, serializers.Serializer):
    login = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)


class AuthCodeVerifyInSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=256)
    code = serializers.CharField(max_length=256)
