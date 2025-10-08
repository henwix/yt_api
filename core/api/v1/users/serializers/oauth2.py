from rest_framework import serializers


class OAuth2ConnectSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text='OAuth2 code')
    state = serializers.CharField(required=True, help_text='OAuth2 state')
    scope = serializers.CharField(required=False, help_text='OAuth2 scope')
    prompt = serializers.CharField(required=False, help_text='OAuth2 prompt')


class AuthUrlSerializer(serializers.Serializer):
    auth_url = serializers.URLField(help_text='URL for oauth2 authorization')


class OAuth2ConnectedProvidersSerializer(serializers.Serializer):
    connected = serializers.DictField(help_text='All connected services via oauth2')
