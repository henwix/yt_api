from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


@dataclass
class VideoNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video not found'}

    video_id: str = None

    @property
    def message(self):
        return 'Video not found'


@dataclass
class VideoNotFoundInHistoryError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video does not exists or never been in history'}

    video_id: str
    channel_slug: str

    @property
    def message(self):
        return 'Video does not exists or never been in history'


@dataclass
class VideoLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Video like/dislike not found'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return 'Video like/dislike not found'


@dataclass
class ViewExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'View already exists. You can add 1 view per 24h.'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return 'View already exists. You can add 1 view per 24h.'


@dataclass
class VideoIdNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'To add or delete video from history you need to provide "video_id"'}

    @property
    def message(self):
        return 'The video_id query param was not provided in request'
