from core.apps.channels.entities.channels import ChannelEntity
from core.apps.channels.models import Channel


def channel_from_entity(channel: ChannelEntity) -> Channel:
    return Channel(
        pk=channel.id,
        slug=channel.slug,
        user_id=channel.user_id,
        name=channel.name,
        description=channel.description,
        country=channel.country,
        avatar_s3_key=channel.avatar_s3_key,
    )


def channel_to_entity(channel: Channel) -> ChannelEntity:
    return ChannelEntity(
        id=channel.pk,
        slug=channel.slug,
        name=channel.name,
        description=channel.description,
        user_id=channel.user_id,
        country=channel.country,
        avatar_s3_key=channel.avatar_s3_key,
    )
