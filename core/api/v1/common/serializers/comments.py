from rest_framework import serializers


class PkParameterSerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class VideoIdParameterSerializer(serializers.Serializer):
    video_id = serializers.CharField(max_length=11, help_text='Video ID')


class LikeSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True, required=False, help_text='Positive of negative reaction')


class PostLikeSerializer(LikeSerializer):
    post_id = serializers.UUIDField(help_text='Post ID')


class VideoLikeSerializer(LikeSerializer, VideoIdParameterSerializer):
    ...


class PkLikeSerializer(LikeSerializer, PkParameterSerializer):
    ...
