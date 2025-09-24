from rest_framework import serializers

from core.api.v1.common.serializers.serializers import CaptchaSerializer


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256)


class AuthInSerializer(CaptchaSerializer, serializers.Serializer):
    login = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)


class AuthCodeVerifyInSerializer(EmailSerializer, serializers.Serializer):
    code = serializers.CharField(max_length=256)
