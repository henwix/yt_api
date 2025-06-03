from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    #  TODO: Move this logic into validators
    def create(self, validated_data):
        request = self.context.get('request')
        user_channel = request.user.channel

        #  check if user's limit report have reached 10
        user_reports = VideoReport.objects.filter(
            author=user_channel, created_at__gt=timezone.now() - timedelta(days=1),
        ).count()
        if user_reports >= 10:
            raise ValidationError('You have reached the limit of reports: 10/day')

        #  create a new report and change 'is_reported' video field if the video have more than 10 reports
        with transaction.atomic():
            validated_data['author'] = user_channel
            report_instance = super().create(validated_data)
            video = report_instance.video

            reports_count = VideoReport.objects.filter(video=video).count()
            if reports_count >= 10 and not video.is_reported:
                Video.objects.filter(video_id=video.video_id, is_reported=False).update(is_reported=True)

            return report_instance
