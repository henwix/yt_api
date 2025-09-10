from rest_framework import serializers


class PlaylistIdParameterSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=32, error_messages={'required': 'This URL parameter is required.'})
