import logging
import os

import boto3
from celery import shared_task
from project.containers import get_container

from .repositories.channels import BaseChannelAvatarRepository, BaseChannelRepository

log = logging.getLogger(__name__)


@shared_task
def delete_channel_files_task(files):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_S3_REGION_NAME'),
    )
    try:
        response = s3_client.delete_objects(Bucket='django-henwix-bucket', Delete={'Objects': files})
        return f'Files successfully deleted: {len(response.get("Deleted", []))}'

    except Exception as e:
        return f'Failed to delete files: {e}'


@shared_task(bind=True, max_retries=3)
def delete_channel_avatar(self, user_id: int):
    container = get_container()
    avatar_repository = container.resolve(BaseChannelAvatarRepository)
    channel_repository = container.resolve(BaseChannelRepository)

    channel = channel_repository.get_channel_by_id(user_id)

    try:
        log.info('Trying to delete channel avatar: %s', channel.slug)
        avatar_repository.delete_avatar(channel)
    except Exception as e:
        log.error("AWS can't delete avatar for channel: %s. Error: %s", channel.slug, e)
        raise self.retry(countdown=5)
    else:
        log.info('%s channel avatar successfully deleted', channel.slug)
