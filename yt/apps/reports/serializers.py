from rest_framework import serializers

from apps.videos.models import Video

from .models import VideoReport


class VideoReportSerializer(serializers.ModelSerializer):
    report_link = serializers.HyperlinkedIdentityField(
        view_name='v1:reports:video-reports-detail',
        many=False,
    )
    video = serializers.SlugRelatedField(queryset=Video.objects.all(), slug_field='video_id', write_only=True)
    video_link = serializers.HyperlinkedRelatedField(
        view_name='v1:videos:video-detail',
        read_only=True,
        many=False,
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
        source='video',
    )
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channel-show',
        read_only=True,
        many=False,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
    )

    class Meta:
        model = VideoReport
        fields = ['report_link', 'video', 'video_link', 'author_link', 'reason', 'description']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user.channel
        return super().create(validated_data)
