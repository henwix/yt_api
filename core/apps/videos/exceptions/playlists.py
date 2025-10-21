from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions.exceptions import ServiceException


@dataclass
class PlaylistIdNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'detail': "'playlist_id' parameter was not provided"}


@dataclass
class PlaylistNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Playlist not found'}

    playlist_id: str


@dataclass
class VideoNotInPlaylistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'detail': 'Video does not exist in playlist'}

    playlist_id: str
    video_id: str


@dataclass
class PlaylistPermissionError(ServiceException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': 'You do not have permission to perform actions with this playlist'}

    playlist_id: str
    channel_id: str
