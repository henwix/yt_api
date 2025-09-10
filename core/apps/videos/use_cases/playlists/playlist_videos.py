from dataclasses import dataclass
from typing import Iterable

from core.apps.channels.services.channels import BaseChannelService
from core.apps.users.entities import UserEntity
from core.apps.videos.models import Video
from core.apps.videos.services.videos import (
    BasePlaylistPrivatePermissionValidatorService,
    BaseVideoPlaylistService,
)


@dataclass
class GetPlaylistVideosUseCase:
    playlist_service: BaseVideoPlaylistService
    playlist_validator_service: BasePlaylistPrivatePermissionValidatorService
    channel_service: BaseChannelService

    def execute(self, playlist_id: str, user: UserEntity) -> Iterable[Video]:
        playlist = self.playlist_service.get_playlist_by_id_or_error(playlist_id=playlist_id)
        channel = self.channel_service.get_channel_by_user_or_none(user=user)

        self.playlist_validator_service.validate(playlist, channel)

        return self.playlist_service.get_playlist_videos(playlist.id)
