from rest_framework import serializers


class AuthSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)
