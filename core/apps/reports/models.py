from django.db import models

from core.apps.channels.models import Channel
from core.apps.videos.models import Video


class VideoReport(models.Model):
    class ReportReasons(models.TextChoices):
        VIOLENT_OR_REPULSIVE_CONTENT = 'VIOLENT_OR_REPULSIVE_CONTENT', 'Violent or repulsive content'
        SEXUAL_CONTENT = 'SEXUAL_CONTENT', 'Sexual content'
        HATEFUL_OR_ABUSIVE_CONTENT = 'HATEFUL_OR_ABUSIVE_CONTENT', 'Hateful or abusive content'
        HARASSMENT_OR_BULLYING = 'HARASSMENT_OR_BULLYING', 'Harassment or bullying'
        HARMFUL_OR_DANGEROUS_ACTS = 'HARMFUL_OR_DANGEROUS_ACTS', 'Harmful or dangerous acts'
        MISINFORMATION = 'MISINFORMATION', 'Misinformation'
        CHILD_ABUSE = 'CHILD_ABUSE', 'Child abuse'
        PROMOTES_TERRORISM = 'PROMOTES_TERRORISM', 'Promotes terrorism'
        SPAM_OR_MISLEADING = 'SPAM_OR_MISLEADING', 'Spam or misleading'
        LEGAL_ISSUE = 'LEGAL_ISSUE', 'Legal issue'
        CAPTIONS_ISSUE = 'CAPTIONS_ISSUE', 'Captions issue'

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    author = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(choices=ReportReasons.choices, max_length=28, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report №{self.pk}'
