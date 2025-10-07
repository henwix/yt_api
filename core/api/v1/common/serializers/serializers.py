from django.conf import settings
from rest_framework import serializers


class LikeCreateInSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True)


class LikeCreateOutSerializer(serializers.Serializer):
    detail = serializers.CharField()
    is_like = serializers.BooleanField()


class JWTOutSerializer(serializers.Serializer):
    access = serializers.CharField(help_text='JWT access token')
    refresh = serializers.CharField(help_text='JWT refresh token')


class DetailOutSerializer(serializers.Serializer):
    detail = serializers.CharField(max_length=256, help_text='Detail response message')


class UrlSerializer(serializers.Serializer):
    url = serializers.CharField()


class SParameterSerializer(serializers.Serializer):
    s = serializers.CharField(max_length=40, error_messages={'required': 'This query parameter is required.'})


class VParameterSerializer(serializers.Serializer):
    v = serializers.CharField(max_length=11, error_messages={'required': 'This query parameter is required.'})


class UUID4CodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        min_length=32,
        max_length=32,
        help_text='The UUID4 code that was generated for the user',
    )


class CaptchaSerializer(serializers.Serializer):
    captcha_token = serializers.CharField(help_text='Captcha token', write_only=True)
    captcha_version = serializers.ChoiceField(
        choices=settings.CAPTCHA_VERSIONS.choices, help_text='Captcha version', write_only=True,
    )
