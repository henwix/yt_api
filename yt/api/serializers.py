import uuid
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Channel, Video

"""
TODO:    - likes to comments and posts: add, delete
TODO:    - comments: add, delete
TODO:    - posts: add, detail, delete
TODO:    - subscriptions
TODO:    - watch history
TODO:    - playlists
TODO:    - следить за запросами в БД
"""


class VideoSerializer(serializers.ModelSerializer):
    """
    Video serializer for video creation, updating and retrieving.
    """

    author_name = serializers.StringRelatedField(source='author')
    author_link = serializers.HyperlinkedRelatedField(
        view_name='api:channel-show',
        lookup_field = 'slug',
        lookup_url_kwarg = 'slug',
        source='author',
        read_only=True
    )
    video_link = serializers.HyperlinkedIdentityField(
        view_name='api:video-detail',
        lookup_field = 'video_id',
        lookup_url_kwarg = 'video_id',
    )
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'name', 
            'description', 
            'status', 
            'video_link',
            'yt_link',
            'author_name',
            'author_link',
            'created_at',
            'status',
            'likes_count',
            'views_count',
        ]
        read_only_fields = ['created_at', 'yt-link']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user.channel

        return super().create(validated_data)


class VideoPreviewSerializer(serializers.ModelSerializer):
    """
    Video serializer for preview.
    """

    video_link = serializers.HyperlinkedIdentityField(
        view_name='api:video-detail',
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
    )
    views_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'name',
            'created_at',
            'yt_link',
            'video_link',
            'views_count'
        ]


class ChannelSerializer(serializers.ModelSerializer):
    """
    Channel serializer for user creation and detail endpoints.
    """

    class Meta:
        model = Channel
        fields = ['name', 'slug', 'description', 'country']
        read_only_fields = ['user']
        extra_kwargs = {
            'name': {'required': False, },
        }


class ChannelAndVideosSerializer(ChannelSerializer):
    """
    Channel serializer for detail endpoints with extra video field.
    Used in 'ChannelMainView'.
    """

    videos = VideoPreviewSerializer(read_only=True, many=True)

    class Meta:
        model = ChannelSerializer.Meta.model
        fields = ChannelSerializer.Meta.fields + ['videos']


class ChannelAboutSerializer(serializers.ModelSerializer):
    """
    Channel serializer for /about/ page.
    """

    total_videos = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)
    total_subs = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    channel_link = serializers.HyperlinkedIdentityField(
        view_name='api:channel-show',
        lookup_field='slug',
        lookup_url_kwarg='slug',
    )

    class Meta:
        model = Channel
        fields = [
            'description', 
            'date_joined', 
            'country', 
            'channel_link', 
            'total_views', 
            'total_videos',
            'total_subs'
        ]


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Custom serializer for user creation. Inherited from UserCreateSerializer by Djoser.
    Added Channel instance creation in create() method.
    """

    def create(self, validated_data):
        channel_data = validated_data.pop('channel', {})

        # if 'name' field is missing in data, it'll be created based on username
        channel_data.setdefault('name', validated_data.get('username'))

        # if 'slug' fields in missing in data, it'll be created based on 'name' + uuid
        if not channel_data.get('slug'):
            base_slug = channel_data.get('name').replace(' ', '')
            unique_slug = base_slug

            if Channel.objects.filter(slug=unique_slug).exists():
                unique_slug = base_slug + '_' + uuid.uuid4().hex[:8]
    
            channel_data['slug'] = unique_slug
        else:
            channel_data['slug'] = channel_data.get('slug')

        # create user instance
        user = super().create(validated_data)
        
        # add created user in channel_data to provide 'author' field
        channel_data['user'] = user

        # create channel
        Channel.objects.create(**channel_data)

        return user
    
    def validate(self, attrs):
        """
        Need to .pop 'channel' attribute to fix error of unexpected field
        """
        
        channel_data = attrs.pop('channel', {})
        attrs = super().validate(attrs)
        attrs['channel'] = channel_data

        return attrs

    def get_fields(self):
        """
        Custom 'get_fields' method to add nested 'ChannelSerializer serializer'. 
        """
        
        fields = super().get_fields()
        fields['channel'] = ChannelSerializer()

        return fields


class CustomUserSerializer(UserSerializer):
    """
    Inherit from base UserSerializer from Djoser.
    Added ChannelSerializer to get_fields_method.
    """

    def get_fields(self):
        fields = super().get_fields()
        fields['channel'] = ChannelSerializer(read_only=True)

        return fields