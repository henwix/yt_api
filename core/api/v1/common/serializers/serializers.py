from rest_framework import serializers


class LikeCreateInSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True)


class LikeCreateOutSerializer(serializers.Serializer):
    is_like = serializers.BooleanField()
    status = serializers.CharField()


class LikeDeleteOutSerializer(serializers.Serializer):
    status = serializers.CharField()
