from rest_framework import serializers

from ..models import (
    Playlist,
    Video,
    VideoComment,
    VideoHistory,
)


class VideoCommentSerializer(serializers.ModelSerializer):
    video = serializers.SlugRelatedField(queryset=Video.objects.all(), slug_field='video_id', write_only=True)
    author = serializers.HiddenField(default=None)
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        many=False,
        read_only=True,
    )
    author_slug = serializers.CharField(source='author.slug', read_only=True)
    update_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:videos-comment-detail',
        many=False,
        read_only=True,
    )
    likes_count = serializers.IntegerField(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VideoComment
        fields = [
            'pk',
            'author_slug',
            'author_link',
            'author',
            'video',
            'text',
            'update_link',
            'reply_level',
            'is_updated',
            'created_at',
            'likes_count',
            'replies_count',
            'comment',
        ]
        read_only_fields = ['pk', 'is_updated', 'created_at']

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['author'] = user.channel

        return super().create(validated_data)


class VideoSerializer(serializers.ModelSerializer):
    """Video serializer for video creation, updating and retrieving."""

    author_name = serializers.StringRelatedField(source='author')
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        read_only=True,
    )
    video_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:videos-detail',
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
    )
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    subs_count = serializers.IntegerField(read_only=True)

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
            's3_bucket',
        ]
        read_only_fields = [
            'created_at',
            'yt-link',
            'upload_status',
            'is_reported',
            'upload_id',
            's3_key',
            's3_bucket',
        ]


class VideoPreviewSerializer(serializers.ModelSerializer):
    """Video serializer for preview."""

    video_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:videos-detail',
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
    )
    views_count = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.slug')
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        source='author',
        many=False,
        read_only=True,
        lookup_field='slug',
        lookup_url_kwarg='slug',
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
        ]


class VideoHistorySerializer(serializers.ModelSerializer):
    video = VideoPreviewSerializer(many=False, read_only=True)

    class Meta:
        model = VideoHistory
        fields = ['video', 'watched_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['channel'] = request.user.channel

        return super().create(validated_data)


class PlaylistPreviewSerializer(serializers.ModelSerializer):
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    channel_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        many=False,
        read_only=True,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='channel',
    )
    playlist_link = serializers.HyperlinkedIdentityField(
        view_name='v1:videos:playlists-detail',
        lookup_field='id',
        lookup_url_kwarg='id',
        read_only=True,
    )
    videos_count = serializers.IntegerField(read_only=True)

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
    videos = VideoPreviewSerializer(many=True, read_only=True)

    class Meta:
        model = PlaylistPreviewSerializer.Meta.model
        fields = ['title', 'description', 'status', 'channel_name', 'channel_link', 'videos_count', 'videos']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['channel'] = request.user.channel

        return super().create(validated_data)
