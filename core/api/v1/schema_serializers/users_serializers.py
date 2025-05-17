from rest_framework import serializers

from drf_spectacular.utils import PolymorphicProxySerializer


class OTPEmailSentSchemaSerializer(serializers.Serializer):
    status = serializers.CharField(default="Email successfully sent")


class JWTTokensCreatedSchemaSerializer(serializers.Serializer):
    refresh = serializers.CharField(default="string")
    access = serializers.CharField(default="string")


UsersLoginProxy = PolymorphicProxySerializer(
    component_name='OKResponse',
    serializers=[
        OTPEmailSentSchemaSerializer,
        JWTTokensCreatedSchemaSerializer,
    ],
    resource_type_field_name='type',
)
