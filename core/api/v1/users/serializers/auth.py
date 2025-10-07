from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from rest_framework import serializers

from core.api.v1.common.serializers.serializers import CaptchaSerializer


class EmailSerializer(serializers.Serializer):
    """Email serializer without value unique validator."""
    email = serializers.EmailField(max_length=256, help_text="User\'s email address")


class AuthInSerializer(CaptchaSerializer, serializers.Serializer):
    login = serializers.CharField(max_length=256, help_text="User's email or username")
    password = serializers.CharField(max_length=128, help_text="User's password")

    def validate_login(self, value):
        username_validator = UnicodeUsernameValidator()
        email_validator = EmailValidator()

        try:
            email_validator(value=value)
        except ValidationError:
            username_validator(value=value)
        return value


class AuthCodeVerifyInSerializer(EmailSerializer, serializers.Serializer):
    code = serializers.CharField(max_length=256)
