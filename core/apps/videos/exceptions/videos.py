from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.videos.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class VideoNotFoundByVideoIdError(ServiceException):
    default_code = ErrorCodes.VIDEO_NOT_FOUND_BY_VIDEO_ID
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str


@dataclass
class VideoIdNotProvidedError(ServiceException):
    default_code = ErrorCodes.VIDEO_ID_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class VideoNotFoundInHistoryError(ServiceException):
    default_code = ErrorCodes.VIDEO_NOT_FOUND_IN_HISTORY
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str
    channel_slug: str


@dataclass
class VideoLikeNotFoundError(ServiceException):
    default_code = ErrorCodes.VIDEO_LIKE_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str
    video_id: str


@dataclass
class ViewExistsError(ServiceException):
    default_code = ErrorCodes.VIEW_EXISTS
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    channel_slug: str
    video_id: str


@dataclass
class VideoAuthorNotMatchError(ServiceException):
    default_code = ErrorCodes.VIDEO_AUTHOR_NOT_MATCH
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str
    author_id: str


@dataclass
class PrivateVideoPermissionError(ServiceException):
    default_code = ErrorCodes.PRIVATE_VIDEO_PERMISSION_ERROR
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str
    channel_id: str | None


@dataclass
class PrivateVideoOrUploadingError(ServiceException):
    default_code = ErrorCodes.PRIVATE_VIDEO_OR_UPLOADING
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    video_id: str
    channel_id: int
