from rest_framework import serializers

from core.api.v1.common.serializers.upload_serializers import FilenameSerializer
from core.apps.videos.models import (
    Playlist,
    Video,
    VideoComment,
)


class VideoCommentSerializer(serializers.ModelSerializer):
    video = serializers.SlugRelatedField(
        queryset=Video.objects.all(),
        slug_field='video_id',
        write_only=True,
        help_text='Video slug',
    )
    author = serializers.HiddenField(default=None)
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        many=False,
        read_only=True,
        help_text='Comment author channel link',
    )
    author_slug = serializers.CharField(source='author.slug', read_only=True, help_text='Comment author channel slug')
    likes_count = serializers.IntegerField(read_only=True, help_text='Total number of likes')
    replies_count = serializers.IntegerField(read_only=True, help_text='Total number of replies')

    class Meta:
        model = VideoComment
        fields = [
            'pk',
            'author_slug',
            'author_link',
            'author',
            'video',
            'text',
            # 'update_link',
            'reply_level',
            'is_updated',
            'created_at',
            'likes_count',
            'replies_count',
            'reply_comment',
        ]
        read_only_fields = ['pk', 'is_updated', 'created_at', 'reply_level']


class CommentCreatedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField(help_text='Comment content')
    reply_level = serializers.IntegerField(help_text='Level of reply')
    created_at = serializers.DateTimeField(help_text='Date when the comment was created')


class VideoCreateSerializer(FilenameSerializer, serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'name',
            'description',
            'status',
            'filename',
        ]


class VideoSerializer(serializers.ModelSerializer):
    """Video serializer for video creation, updating and retrieving."""

    author_name = serializers.StringRelatedField(source='author.name', help_text='Video author name')
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        read_only=True,
        help_text='Video author channel link',
    )
    video_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:videos-detail',
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
        help_text='Video link',
    )
    likes_count = serializers.IntegerField(read_only=True, help_text='Total number of likes')
    views_count = serializers.IntegerField(read_only=True, help_text='Total number of views')
    comments_count = serializers.IntegerField(read_only=True, help_text='Total number of comments')
    subs_count = serializers.IntegerField(read_only=True, help_text='Total number of subs')

    class Meta:
        model = Video
        fields = [
            'name',
            'description',
            'video_link',
            'likes_count',
            'views_count',
            'comments_count',
            'subs_count',
            'author_name',
            'author_link',
            'is_reported',
            'created_at',
            'status',
            'upload_status',
            'upload_id',
            's3_key',
        ]
        read_only_fields = [
            'created_at',
            'upload_status',
            'is_reported',
            'upload_id',
            's3_key',
        ]


class VideoPreviewSerializer(serializers.ModelSerializer):
    """Video serializer for preview."""

    video_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:videos-detail',
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
        help_text='Video link',
    )
    views_count = serializers.IntegerField(read_only=True, required=False, help_text='Total number of views')
    author_name = serializers.CharField(source='author.slug', help_text='Video author name')
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        source='author',
        many=False,
        read_only=True,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        help_text='Video author channel link',
    )

    class Meta:
        model = Video
        fields = [
            'name',
            'created_at',
            'video_link',
            'author_name',
            'author_link',
            'views_count',
            'upload_status',
            'status',
            's3_key',
        ]


class PlaylistPreviewSerializer(serializers.ModelSerializer):
    channel_name = serializers.CharField(
        source='channel.name',
        read_only=True,
        help_text='Playlist author channel name',
    )
    channel_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        many=False,
        read_only=True,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='channel',
        help_text='Playlist author channel link',
    )
    playlist_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:playlists-detail',
        lookup_field='id',
        lookup_url_kwarg='id',
        read_only=True,
        help_text='Playlist link',
    )
    videos_count = serializers.IntegerField(read_only=True, help_text='Total number of videos')

    class Meta:
        model = Playlist
        fields = [
            'title',
            'status',
            'playlist_link',
            'channel_name',
            'channel_link',
            'videos_count',
        ]


class PlaylistSerializer(PlaylistPreviewSerializer):
    class Meta:
        model = PlaylistPreviewSerializer.Meta.model
        fields = [
            'title',
            'description',
            'playlist_link',
            'status',
            'channel_name',
            'channel_link',
            'videos_count',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['channel'] = request.user.channel

        return super().create(validated_data)


class UpdatePlaylistSerializer(PlaylistSerializer):
    class Meta:
        model = PlaylistSerializer.Meta.model
        fields = [
            'title',
            'description',
            'playlist_link',
            'status',
            'channel_name',
            'channel_link',
            'videos_count',
        ]
