from rest_framework import serializers

from core.api.v1.videos.serializers.video_serializers import VideoPreviewSerializer
from core.apps.videos.models import VideoHistory


class VideoHistorySerializer(serializers.ModelSerializer):
    video = VideoPreviewSerializer(many=False, read_only=True)

    class Meta:
        model = VideoHistory
        fields = ['watched_at', 'video']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['channel'] = request.user.channel

        return super().create(validated_data)
