from dataclasses import dataclass

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.videos.errors import (
    ErrorCodes,
    ERRORS,
)


@dataclass
class PlaylistIdNotProvidedError(ServiceException):
    default_code = ErrorCodes.PLAYLIST_ID_NOT_PROVIDED
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}


@dataclass
class PlaylistNotFoundError(ServiceException):
    default_code = ErrorCodes.PLAYLIST_NOT_FOUND
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    playlist_id: str


@dataclass
class VideoNotInPlaylistError(ServiceException):
    default_code = ErrorCodes.VIDEO_NOT_IN_PLAYLIST
    status_code = ERRORS[default_code]['status_code']
    default_detail = {'detail': ERRORS[default_code]['message']}

    playlist_id: str
    video_id: str
