from rest_framework import serializers


class LikeCreateInSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True)


class LikeCreateOutSerializer(serializers.Serializer):
    status = serializers.CharField()
    is_like = serializers.BooleanField()


class LikeDeleteOutSerializer(serializers.Serializer):
    status = serializers.CharField()
