from rest_framework import serializers
from .models import Channel
from apps.videos.serializers import VideoPreviewSerializer


"""
TODO:    - likes to comments and posts: add, delete
TODO:    - comments: add, delete
TODO:    - posts: add, detail, delete
TODO:    - subscriptions
TODO:    - watch history
TODO:    - playlists
TODO:    - следить за запросами в БД
"""


class ChannelSerializer(serializers.ModelSerializer):
    """
    Channel serializer for user creation and detail endpoints.
    """

    class Meta:
        model = Channel
        fields = ["name", "slug", "description", "country"]
        read_only_fields = ["user"]
        extra_kwargs = {
            "name": {
                "required": False,
            },
        }


class ChannelAndVideosSerializer(ChannelSerializer):
    """
    Channel serializer for detail endpoints with extra video field.
    Used in 'ChannelMainView'.
    """

    videos = VideoPreviewSerializer(read_only=True, many=True)

    class Meta:
        model = ChannelSerializer.Meta.model
        fields = ChannelSerializer.Meta.fields + ["videos"]


class ChannelAboutSerializer(serializers.ModelSerializer):
    """
    Channel serializer for /about/ page.
    """

    total_videos = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)
    total_subs = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    channel_link = serializers.HyperlinkedIdentityField(
        view_name="v1:channels:channel-show",
        lookup_field="slug",
        lookup_url_kwarg="slug",
    )

    class Meta:
        model = Channel
        fields = ["description", "date_joined", "country", "channel_link", "total_views", "total_videos", "total_subs"]
