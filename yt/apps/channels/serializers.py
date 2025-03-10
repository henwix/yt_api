from rest_framework import serializers
from .models import Channel, SubscriptionItem
from apps.videos.serializers import VideoPreviewSerializer


"""
TODO:    - likes to comments and posts: add, delete
TODO:    - posts: add, detail, delete
TODO:    - watch history
TODO:    - playlists
"""


class ChannelSerializer(serializers.ModelSerializer):
    """
    Channel serializer for user creation and detail endpoints.
    """
    
    class Meta:
        model = Channel
        fields = ["name", "slug", "description", "country", "channel_avatar"]
        read_only_fields = ["user"]
        extra_kwargs = {
            "name": {
                "required": False,
            },
        }

    def validate_channel_avatar(self, value):
        if value and value.size > 1 * 1024 * 1024:
            raise serializers.ValidationError('File size must be less than 1MB.')

        return value
        

    def update(self, instance, validated_data):
        uploaded_avatar = validated_data.get('channel_avatar')

        if uploaded_avatar and instance.channel_avatar:
            instance.channel_avatar.delete(save=False)
        
        if uploaded_avatar is None:
            validated_data.pop('channel_avatar')

        return super().update(instance, validated_data)


class ChannelAndVideosSerializer(ChannelSerializer):
    """
    Channel serializer for detail endpoints with extra video field.
    Used in 'ChannelMainView'.
    """

    videos = VideoPreviewSerializer(read_only=True, many=True)
    subs_count=serializers.IntegerField(read_only=True)

    class Meta:
        model = ChannelSerializer.Meta.model
        fields = ChannelSerializer.Meta.fields + ['subs_count', "videos"]


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


class SubscriptionSerializer(serializers.ModelSerializer):
    sub_slug = serializers.CharField(source='subscriber.slug', read_only=True)
    sub_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channel-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='subscriber',
        read_only=True
    )

    class Meta:
        model = SubscriptionItem
        fields = ['sub_slug', 'sub_link', 'created_at']