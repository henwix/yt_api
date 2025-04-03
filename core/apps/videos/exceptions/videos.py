from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class VideoNotFound(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video not found'}

    video_id: str

    @property
    def message(self):
        return f'Video {self.video_id} not found'


@dataclass
class LikeNotFound(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Like/dislike not found'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return f'Like/dislike by {self.channel_slug} for video {self.video_id} not found'


@dataclass
class ViewExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'View already exists. You can add 1 view per 24h.'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return f'View by {self.channel_slug} for video {self.video_id} already exists'
