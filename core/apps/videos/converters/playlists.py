from core.apps.common.enums import EntityStatus
from core.apps.videos.converters.videos import video_to_entity
from core.apps.videos.entities.playlists import (
    PlaylistEntity,
    PlaylistItemEntity,
)
from core.apps.videos.entities.videos import VideoEntity
from core.apps.videos.models import (
    Playlist,
    PlaylistItem,
)


def convert_playlist_videos_to_entity(playlist: Playlist) -> list[VideoEntity] | EntityStatus:
    if hasattr(playlist, '_prefetched_objects_cache') and 'video' in playlist._prefetched_objects_cache:
        return [video_to_entity(video) for video in playlist.videos.all()]
    return EntityStatus.NOT_LOADED


def playlist_from_entity(playlist: PlaylistEntity) -> Playlist:
    return Playlist(
        pk=playlist.id,
        channel_id=playlist.channel_id,
        title=playlist.title,
        description=playlist.description,
        status=playlist.status,
    )


def playlist_to_entity(playlist: Playlist) -> PlaylistEntity:
    return PlaylistEntity(
        id=playlist.pk,
        channel_id=playlist.channel_id,
        videos=convert_playlist_videos_to_entity(playlist),
        title=playlist.title,
        description=playlist.description,
        status=playlist.status,
    )


def playlist_item_from_entity(playlist_item: PlaylistItemEntity) -> PlaylistItem:
    return PlaylistItem(
        pk=playlist_item.id,
        playlist_id=playlist_item.playlist_id,
        video_id=playlist_item.video_id,
    )


def playlist_item_to_entity(playlist_item: PlaylistItem) -> PlaylistItemEntity:
    return PlaylistItemEntity(
        id=playlist_item.pk,
        playlist_id=playlist_item.playlist_id,
        video_id=playlist_item.video_id,
    )
