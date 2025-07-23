from rest_framework import serializers


class CommentIdParameterSerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class LikeSerializer(serializers.Serializer):
    is_like = serializers.BooleanField(default=True, required=False)


class PostLikeSerializer(LikeSerializer):
    post_id = serializers.UUIDField()


class CommentLikeSerializer(LikeSerializer):
    pk = serializers.IntegerField()
