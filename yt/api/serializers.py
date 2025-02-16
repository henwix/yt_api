import uuid
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Channel, Video
from django.utils.text import slugify

"""
TODO:    - searching videos
TODO:    - videos: watching, edit/delete
TODO:    - likes: add, delete
TODO:    - comments: add, delete
TODO:    - posts: add, detail, delete
TODO:    - subscriptions
TODO:    - playlists
TODO:    - следить за запросами в БД
"""


class VideoSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source='author')

    class Meta:
        model = Video
        fields = [
            'name', 
            'description', 
            'status', 
            'yt_link', 
            'author_name',
            'created_at', 
            'yt_link', 
            'status',
            'likes_count'
        ]
        read_only_fields = ['created_at', 'yt-link', 'get_likes_count']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user.channel

        return super().create(validated_data)

    

class ChannelSerializer(serializers.ModelSerializer):
    """
    Channel serializer for user creation and detail endpoints
    """

    videos = VideoSerializer(read_only=True, many=True)

    class Meta:
        model = Channel
        fields = ['name', 'slug', 'description', 'videos']
        read_only_fields = ['user']
        extra_kwargs = {
            'name': {'required': False, },
        }


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Inherited from base UserCreateSerializer from Djoser.
    Added Channel model instance creation in create() method.
    """

    def create(self, validated_data):
        channel_data = validated_data.pop('channel', {})

        # if 'name' field is missing in data, it'll be created based on username
        channel_data.setdefault('name', validated_data.get('username'))

        # if 'slug' fields in missing in data, it'll be created based on 'name' + uuid
        if not channel_data.get('slug'):
            base_slug = '@' + channel_data.get('name').replace(' ', '')
            unique_slug = base_slug

            if Channel.objects.filter(slug=unique_slug).exists():
                unique_slug = base_slug + '_' + uuid.uuid4().hex[:8]
    
            channel_data['slug'] = unique_slug
        else:
            channel_data['slug'] = '@' + channel_data.get('slug')

        # create user instance
        user = super().create(validated_data)
        
        # add created user in channel_data to provide 'author' field
        channel_data['user'] = user

        # create channel
        Channel.objects.create(**channel_data)

        return user
    
    def validate(self, attrs):
        """
        Need to .pop 'channel' attribute to fix error
        """
        
        channel_data = attrs.pop('channel', {})
        attrs = super().validate(attrs)
        attrs['channel'] = channel_data

        return attrs

    def get_fields(self):
        """
        New field to serializer for Channel creation
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