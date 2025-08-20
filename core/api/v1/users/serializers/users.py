import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

from djoser.conf import settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
    UserCreateSerializer,
    UsernameResetConfirmSerializer,
    UserSerializer,
    ValidationError,
)

from core.api.v1.channels.serializers import ChannelSerializer
from core.api.v1.common.serializers.serializers import CaptchaTokenSerializer
from core.apps.channels.models import Channel


class CustomUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer):
    def get_fields(self):
        """Custom 'get_fields' method to add nested 'ChannelSerializer
        serializer'."""

        fields = super().get_fields()
        fields['channel'] = ChannelSerializer()

        return fields


class CustomUserCreateSerializer(CaptchaTokenSerializer, UserCreateSerializer):
    """Custom serializer for user creation.

    Inherited from UserCreateSerializer by Djoser. Added Channel
    instance creation in create() method.

    """

    email = serializers.EmailField(required=True)

    class Meta:
        model = UserCreateSerializer.Meta.model
        fields = ('captcha_token', 'captcha_version') + UserCreateSerializer.Meta.fields

    def create(self, validated_data):
        channel_data = validated_data.pop('channel', {})

        # if 'name' field is missing in data, it'll be created based on username
        channel_data.setdefault('name', validated_data.get('username'))

        # if 'slug' fields in missing in data, it'll be created based on 'name' + uuid
        if not channel_data.get('slug'):
            base_slug = channel_data.get('name').replace(' ', '')
            unique_slug = base_slug

            if Channel.objects.filter(slug=unique_slug).exists():
                unique_slug = base_slug + '_' + uuid.uuid4().hex[:8]

            channel_data['slug'] = unique_slug

        try:
            # create user instance
            user = super().create(validated_data)

            # add created user in channel_data to provide 'author' field
            channel_data['user'] = user

            # create channel
            Channel.objects.create(**channel_data)

        except IntegrityError as e:
            raise ValidationError({'detail': str(e)})
        return user

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise ValidationError('A user with that email already exists.')
        return value

    def validate(self, attrs):
        """Need to .pop 'channel' attribute to fix error of unexpected
        field."""

        channel_data = attrs.pop('channel', {})
        attrs.pop('captcha_version')
        attrs.pop('captcha_token')

        attrs = super().validate(attrs)
        attrs['channel'] = channel_data

        return attrs

    def get_fields(self):
        """Custom 'get_fields' method to add nested 'ChannelSerializer
        serializer'."""

        fields = super().get_fields()
        fields['channel'] = ChannelSerializer(required=False)

        return fields


class CustomUserSerializer(UserSerializer):
    """Inherit from base UserSerializer from Djoser.

    Added ChannelSerializer to get_fields_method.

    """

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ('otp_enabled',)
        read_only_fields = ['username']

    def get_fields(self):
        fields = super().get_fields()
        fields['channel'] = ChannelSerializer(read_only=True)

        return fields


class CustomUsernameResetConfirmSerializer(UsernameResetConfirmSerializer):
    """Inherit from base UsernameResetConfirmSerializer from Djoser.

    Add fields 'uid' and 'token' to fix Serializer error where they are
    not displayed in Swagger schema

    """

    class Meta:
        model = UsernameResetConfirmSerializer.Meta.model
        fields = (settings.LOGIN_FIELD, 'uid', 'token')
