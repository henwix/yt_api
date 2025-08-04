from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class VideoNotFoundByVideoIdError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by video_id'}

    video_id: str

    @property
    def message(self):
        return 'Video not found by video_id'


@dataclass
class VideoIdNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': '"video_id" not provided'}

    @property
    def message(self):
        return 'The video_id query param was not provided in request'


@dataclass
class VideoNotFoundInHistoryError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video does not exist in history'}

    video_id: str
    channel_slug: str

    @property
    def message(self):
        return 'Video does not exist in history'


@dataclass
class VideoLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video like/dislike not found'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return 'Video like/dislike not found'


@dataclass
class ViewExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'View already exists, you can add 1 view per 24h'}

    channel_slug: str
    video_id: str

    @property
    def message(self):
        return 'View already exists. You can add 1 view per 24h.'


@dataclass
class VideoAuthorNotMatchError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Video author does not match the current user'}

    video_id: str
    author_id: str

    @property
    def message(self):
        return 'Video author does not match the current user'


@dataclass
class PrivateVideoPermissionError(ServiceException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': 'You do not have permission to access this video'}

    video_id: str
    channel_id: str | None

    @property
    def message(self):
        return 'You do not have permission to access this video'


@dataclass
class PrivateVideoOrUploadingError(ServiceException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': "You can't perform actions if the video is private or still uploading"}

    video_id: str
    channel_id: int

    @property
    def message(self):
        return "You can't perform actions if the video is private or is still uploading"
