from rest_framework import serializers

from core.apps.common.constants import CAPTCHA_VERSIONS


class DetailOutSerializer(serializers.Serializer):
    detail = serializers.CharField(max_length=256, help_text='Detail response message')


class LikeCreateInSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True, help_text='Positive of negative reaction')


class LikeCreateOutSerializer(DetailOutSerializer, LikeCreateInSerializer):
    pass


class JWTOutSerializer(serializers.Serializer):
    access = serializers.CharField(help_text='JWT access token')
    refresh = serializers.CharField(help_text='JWT refresh token')


class UrlSerializer(serializers.Serializer):
    url = serializers.CharField(help_text='URL')


class SParameterSerializer(serializers.Serializer):
    s = serializers.CharField(
        max_length=40,
        error_messages={'required': 'This query parameter is required.'},
        help_text="Parameter identifying channel's slug",
    )


class VParameterSerializer(serializers.Serializer):
    v = serializers.CharField(
        max_length=11,
        error_messages={'required': 'This query parameter is required.'},
        help_text='Parameter identifying video id',
    )


class UUID4CodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        min_length=32,
        max_length=32,
        help_text='The UUID4 code that was generated for the user',
    )


class CaptchaSerializer(serializers.Serializer):
    captcha_token = serializers.CharField(required=False, help_text='Captcha token', write_only=True)
    captcha_version = serializers.ChoiceField(
        required=False,
        choices=CAPTCHA_VERSIONS.choices,
        help_text='Captcha version',
        write_only=True,
    )
