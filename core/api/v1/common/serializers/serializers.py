from rest_framework import serializers


class LikeCreateInSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True)


class LikeCreateOutSerializer(serializers.Serializer):
    status = serializers.CharField()
    is_like = serializers.BooleanField()


class LikeDeleteOutSerializer(serializers.Serializer):
    status = serializers.CharField()


class JWTSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()
