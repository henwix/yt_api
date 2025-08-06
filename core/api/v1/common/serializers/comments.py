from rest_framework import serializers


class PkParameterSerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class VideoIdParameterSerializer(serializers.Serializer):
    video_id = serializers.CharField(max_length=11)


class LikeSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True, required=False)


class PostLikeSerializer(LikeSerializer):
    post_id = serializers.UUIDField()


class VideoLikeSerializer(LikeSerializer, VideoIdParameterSerializer):
    ...


class PkLikeSerializer(LikeSerializer, PkParameterSerializer):
    ...
