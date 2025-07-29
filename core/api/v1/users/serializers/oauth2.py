from rest_framework import serializers


class OAuth2ConnectSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text='OAuth2 code')
    state = serializers.CharField(required=True, help_text='OAuth2 state')
    scope = serializers.CharField(required=False, help_text='OAuth2 scope')
    prompt = serializers.CharField(required=False, help_text='OAuth2 prompt')


class OAuth2ConnectJWTSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class OAuth2ConnectAuthorizedSerializer(serializers.Serializer):
    status = serializers.CharField()
