from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class VideoNotFoundByVideoIdError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video not found by video_id'}

    video_id: str


@dataclass
class VideoIdNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': '"video_id" was not provided'}


@dataclass
class VideoDoesNotExistInHistoryError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video does not exist in history'}

    video_id: str
    channel_slug: str


@dataclass
class VideoLikeNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video like or dislike not found'}

    channel_slug: str
    video_id: str


@dataclass
class ViewExistsError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'View already exists, you can add 1 view per 24h'}

    channel_slug: str
    video_id: str


@dataclass
class VideoAuthorNotMatchError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': 'Video author does not match the current user'}

    video_id: str
    author_id: str


@dataclass
class PrivateVideoPermissionError(ServiceException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': 'You do not have permission to access this video'}

    video_id: str
    channel_id: str | None


@dataclass
class PrivateVideoOrUploadingError(ServiceException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': 'You cannot perform actions if the video is private or still uploading'}

    video_id: str
    channel_id: int
