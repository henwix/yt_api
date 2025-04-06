from dataclasses import dataclass

from rest_framework import status

from core.apps.common.exceptions import ServiceException


class PlaylistIdNotProvidedError(ServiceException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {'error': 'To do something with playlist you need to provide "playlist_id"'}

    @property
    def message(self):
        return 'The playlist_id parameter was not provided in request'


@dataclass
class PlaylistNotFoundError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'error': 'Playlist not found'}

    playlist_id: str

    @property
    def message(self):
        return f'Playlist with id {self.playlist_id} not found'


@dataclass
class VideoNotInPlaylistError(ServiceException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = {'status': 'Video does not exists in playlist'}

    playlist_id: str
    video_id: str

    @property
    def message(self):
        return f'Video {self.video_id} not found in playlist {self.playlist_id}'
