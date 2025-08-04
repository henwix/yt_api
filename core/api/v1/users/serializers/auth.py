from rest_framework import serializers


class AuthInSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)


class AuthCodeVerifyInSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=256)
    code = serializers.CharField(max_length=256)
