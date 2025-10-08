from rest_framework import serializers

from core.apps.reports.models import VideoReport
from core.apps.videos.models import Video


class VideoReportSerializer(serializers.ModelSerializer):
    report_link = serializers.HyperlinkedIdentityField(
        view_name='v1:reports:videos-reports-detail',
        many=False,
        help_text='Link to retrieve details about this report',
    )
    video_slug = serializers.SlugRelatedField(
        queryset=Video.objects.all(),
        slug_field='video_id',
        write_only=True,
        help_text='Video slug',
    )
    video_link = serializers.HyperlinkedRelatedField(
        view_name='v1:videos:videos-detail',
        read_only=True,
        many=False,
        lookup_field='video_id',
        lookup_url_kwarg='video_id',
        source='video',
        help_text='Link to retrieve details about the reported video',
    )
    author_link = serializers.HyperlinkedRelatedField(
        view_name='v1:channels:channels-show',
        read_only=True,
        many=False,
        lookup_field='slug',
        lookup_url_kwarg='slug',
        source='author',
        help_text='Link to retrieve details about the author of this report',
    )

    class Meta:
        model = VideoReport
        fields = ['report_link', 'video_slug', 'video_link', 'author_link', 'reason', 'description']
