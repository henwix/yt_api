from rest_framework import serializers

from core.apps.posts.models import PostCommentItem


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentItem
        fields = ['post', 'reply_comment', 'text']


class CommentRetrieveSerializer(serializers.ModelSerializer):
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        many=False,
        read_only=True,
    )
    author_slug = serializers.CharField(source='author.slug', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PostCommentItem
        fields = [
            'pk',
            'text',
            'reply_level',
            'is_updated',
            'created_at',
            'reply_comment',
            'author_slug',
            'author_link',
            'likes_count',
            'replies_count',
        ]


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentItem
        fields = ['text']
