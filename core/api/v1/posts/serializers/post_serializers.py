from rest_framework import serializers

from core.api.v1.common.serializers.serializers import CaptchaTokenSerializer
from core.apps.posts.models import Post


class PostInSerializer(CaptchaTokenSerializer, serializers.Serializer):
    text = serializers.CharField()


class PostOutSerializer(serializers.Serializer):
    pk = serializers.CharField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'text',
            'post_id',
            'created_at',
        ]
        read_only_fields = [
            'post_id',
            'created_at',
        ]


class PostDetailedSerializer(PostSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_avatar_s3_key = serializers.CharField(source='author.avatar_s3_key', read_only=True)
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        read_only=True,
    )

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields + [
            'likes_count',
            'comments_count',
            'author_name',
            'author_avatar_s3_key',
            'author_link',
        ]
        read_only_fields = PostSerializer.Meta.read_only_fields


class PostUIDSerializer(serializers.Serializer):
    p = serializers.UUIDField()
