from rest_framework import serializers

from core.apps.reports.models import VideoReport
from core.apps.videos.models import Video


class VideoReportSerializer(serializers.ModelSerializer):
    report_link = serializers.HyperlinkedIdentityField(
        view_name='v1:reports:videos-reports-detail',
        many=False,
    )
    video = serializers.SlugRelatedField(queryset=Video.objects.all(), slug_field='video_id', write_only=True)
    video_link = serializers.HyperlinkedRelatedField(
        view_name='v1:videos:videos-detail',
        read_only=True,
        many=False,
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
        source='video',
    )
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        read_only=True,
        many=False,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
    )

    class Meta:
        model = VideoReport
        fields = ['report_link', 'video', 'video_link', 'author_link', 'reason', 'description']
