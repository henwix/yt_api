from logging import Logger

import orjson
import punq
from celery import shared_task

from core.apps.common.services.boto_client import BaseBotoClientService
from core.project.containers import get_container

from .repositories.channels import (
    BaseChannelAvatarRepository,
    BaseChannelRepository,
)


@shared_task(bind=True, max_retries=10)
def delete_channel_files_task(self, files):
    container: punq.Container = get_container()
    boto_service: BaseBotoClientService = container.resolve(BaseBotoClientService)
    logger: Logger = container.resolve(Logger)

    s3_client = boto_service.get_s3_client()

    try:
        logger.info(
            'Trying to delete files',
            extra={'log_meta': orjson.dumps({'number_of_files': len(files)}).decode()},
        )
        response = s3_client.delete_objects(
            Bucket=boto_service.get_bucket_name(),
            Delete={'Objects': files},
        )
    except Exception as error:
        logger.error(
            "AWS S3 can't delete channel files",
            extra={'log_meta': orjson.dumps({'number_of_files': len(files)}).decode(), 'error': error},
        )
        raise self.retry(countdown=5)
    else:
        logger.info(
            'Files successfully deleted',
            extra={'log_meta': orjson.dumps({'number_of_files': len(response.get("Deleted", []))}).decode()},
        )
        return f'{len(response.get("Deleted", []))} files successfully deleted'


@shared_task(bind=True, max_retries=3)
def delete_channel_avatar(self, user_id: int):
    container: punq.Container = get_container()
    avatar_repository = container.resolve(BaseChannelAvatarRepository)
    channel_repository = container.resolve(BaseChannelRepository)
    logger: Logger = container.resolve(Logger)

    channel = channel_repository.get_channel_by_id(user_id)

    try:
        logger.info(
            'Trying to delete channel avatar',
            extra={'log_meta': orjson.dumps({'channel': channel.slug}).decode()},
        )
        avatar_repository.delete_avatar(channel)
    except Exception as error:
        logger.error(
            "AWS can't delete channel avatar",
            extra={'log_meta': orjson.dumps({'channel': channel.slug}).decode(), 'error': error},
        )
        raise self.retry(countdown=5)
    else:
        logger.info(
            'Channel avatar successfully deleted',
            extra={'log_meta': orjson.dumps({'channel': channel.slug}).decode()},
        )
