from logging import Logger

import orjson
import punq
from botocore.exceptions import ClientError
from celery import shared_task

from core.apps.videos.providers.videos import BaseBotoFileProvider
from core.project.containers import get_container


@shared_task(bind=True, max_retries=10)
def delete_s3_video_task(self, key: str):
    container: punq.Container = get_container()
    boto_provider: BaseBotoFileProvider = container.resolve(BaseBotoFileProvider)
    logger: Logger = container.resolve(Logger)

    try:
        logger.info('Start deleting video from S3', extra={'log_meta': orjson.dumps({'key': key}).decode()})
        boto_provider.delete_object_by_key(key=key)
    except ClientError as error:
        logger.error(
            'Failed to delete video from S3',
            extra={'log_meta': orjson.dumps({'key': key, 'error': str(error)}).decode()},
        )
        raise self.retry(countdown=60)

    logger.info('Video successfully deleted from S3', extra={'log_meta': orjson.dumps({'key': key}).decode()})


@shared_task(bind=True, max_retries=10)
def abort_multipart_upload_task(self, key: str, upload_id: str) -> None:
    container: punq.Container = get_container()
    boto_provider: BaseBotoFileProvider = container.resolve(BaseBotoFileProvider)
    logger: Logger = container.resolve(Logger)

    try:
        logger.info(
            'Start aborting multipart upload from S3',
            extra={'log_meta': orjson.dumps({'key': key, 'upload_id': upload_id}).decode()},
        )
        boto_provider.abort_multipart_upload(key=key, upload_id=upload_id)
    except ClientError as error:
        logger.error(
            'Failed to abort multipart upload from S3',
            extra={
                'log_meta': orjson.dumps(
                    {
                        'key': key,
                        'upload_id': upload_id,
                        'error': str(error),
                    },
                ).decode(),
            },
        )
        raise self.retry(countdown=60)

    logger.info(
        'Multipart upload successfully aborted from S3',
        extra={'log_meta': orjson.dumps({'key': key, 'upload_id': upload_id}).decode()},
    )
