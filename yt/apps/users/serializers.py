from djoser.serializers import UserCreateSerializer, UserSerializer
from apps.channels.models import Channel
from apps.channels.serializers import ChannelSerializer
import uuid


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