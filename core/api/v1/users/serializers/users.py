from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.api.v1.channels.serializers import ChannelSerializer
from core.api.v1.common.serializers.serializers import (
    CaptchaSerializer,
    UUID4CodeSerializer,
)
from core.apps.users.models import CustomUser


class UserSerializer(CaptchaSerializer, serializers.ModelSerializer):
    channel = ChannelSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'otp_enabled', 'password', 'captcha_token', 'captcha_version', 'channel']
        read_only_fields = ['id', 'otp_enabled']
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'otp_enabled']


class PasswordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password']

    def validate_password(self, value):
        validate_password(password=value)
        return value


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email']


class UIDAndCodeConfirmSerializer(UUID4CodeSerializer):
    uid = serializers.CharField(max_length=20)


class PasswordResetConfirmSerializer(UIDAndCodeConfirmSerializer, PasswordUserSerializer):
    class Meta:
        model = CustomUser
        fields = ['uid', 'code', 'password']


class UsernameResetConfirmSerializer(UIDAndCodeConfirmSerializer, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['uid', 'code', 'username']
