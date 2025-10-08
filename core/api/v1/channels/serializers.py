from rest_framework import serializers

from core.api.v1.videos.serializers.video_serializers import VideoPreviewSerializer
from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)


class ChannelSerializer(serializers.ModelSerializer):
    """Channel serializer for user creation and detail endpoints."""

    class Meta:
        model = Channel
        fields = ['name', 'slug', 'description', 'country', 'avatar_s3_key']
        read_only_fields = ['user', 'avatar_s3_key']
        extra_kwargs = {
            'name': {
                'required': False,
            },
            'slug': {
                'required': False,
            },
        }


class ChannelAndVideosSerializer(ChannelSerializer):
    """Channel serializer for detail endpoints with extra video field.

    Used in 'ChannelMainView'.

    """

    videos = VideoPreviewSerializer(read_only=True, many=True, help_text='Channel videos')
    subs_count = serializers.IntegerField(read_only=True, help_text='Total number of subscribers')

    class Meta:
        model = ChannelSerializer.Meta.model
        fields = ChannelSerializer.Meta.fields + ['subs_count', 'videos']


class ChannelAboutSerializer(serializers.ModelSerializer):
    """Channel serializer for /about/ page."""

    total_videos = serializers.IntegerField(read_only=True, help_text='Total number of videos')
    total_views = serializers.IntegerField(read_only=True, help_text='Total number of views')
    total_subs = serializers.IntegerField(read_only=True, help_text='Total number of subscribers')
    date_joined = serializers.DateTimeField(
        source='user.date_joined',
        read_only=True,
        help_text='Date when the channel was created',
    )
    channel_link = serializers.HyperlinkedIdentityField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        help_text='Link to this channel',
    )

    class Meta:
        model = Channel
        fields = ['description', 'date_joined', 'country', 'channel_link', 'total_views', 'total_videos', 'total_subs']


class SubscriptionSerializer(serializers.ModelSerializer):
    sub_slug = serializers.CharField(source='subscriber.slug', read_only=True, help_text='Subscriber slug')
    sub_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='subscriber',
        read_only=True,
        many=False,
        help_text='Subscriber link',
    )

    class Meta:
        model = SubscriptionItem
        fields = ['sub_slug', 'sub_link', 'created_at']


class SubscriptionInSerializer(serializers.Serializer):
    channel_slug = serializers.SlugField(max_length=40, help_text='Channel slug')
