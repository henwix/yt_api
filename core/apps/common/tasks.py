from logging import Logger

import orjson
import punq
from botocore.exceptions import ClientError
from celery import shared_task

from core.apps.common.providers.cache import BaseCacheProvider
from core.apps.common.providers.files import BaseBotoFileProvider
from core.project.containers import get_container


@shared_task(bind=True, max_retries=3)
def test_task(self):
    import random  # noqa

    container = get_container()  
    logger: Logger = container.resolve(Logger)
    logger.info('test task running')

    is_restart = random.choice([True, False])  # noqa
    if is_restart:
        logger.info('Restarting task')
        raise self.retry(countdown=5)
    return 'test task completed successfully'


@shared_task(bind=True, max_retries=10)
def delete_s3_objects_task(self, objects: list[dict]) -> str:
    container: punq.Container = get_container()
    boto_provider: BaseBotoFileProvider = container.resolve(BaseBotoFileProvider)
    logger: Logger = container.resolve(Logger)

    try:
        logger.info(
            'Trying to delete objects from AWS S3',
            extra={'log_meta': orjson.dumps({'number_of_files': len(objects)}).decode()},
        )
        response = boto_provider.delete_objects(
            objects=objects,
        )

    except ClientError as error:
        logger.error(
            "AWS S3 can't delete objects",
            extra={'log_meta': orjson.dumps({'number_of_files': len(objects)}).decode(), 'error': str(error)},
        )
        raise self.retry(countdown=60)

    logger.info(
        'Objects successfully deleted from AWS S3',
        extra={'log_meta': orjson.dumps({'number_of_files': len(response.get("Deleted", []))}).decode()},
    )
    return f'{len(response.get("Deleted", []))} objects successfully deleted from AWS S3'


@shared_task(bind=True, max_retries=10)
def delete_s3_object_task(self, key: str, cache_key: str | None = None) -> str:
    container: punq.Container = get_container()
    boto_provider: BaseBotoFileProvider = container.resolve(BaseBotoFileProvider)
    cache_provider: BaseCacheProvider = container.resolve(BaseCacheProvider)
    logger: Logger = container.resolve(Logger)

    try:
        logger.info('Start deleting object from AWS S3', extra={'log_meta': orjson.dumps({'key': key}).decode()})
        boto_provider.delete_object_by_key(
            key=key,
        )

        if cache_key:
            cache_provider.delete(key=cache_key)
            logger.info(
                'Cache key deleted',
                extra={'log_meta': orjson.dumps({'cache_key': cache_key}).decode()},
            )

    except ClientError as error:
        logger.error(
            'Failed to delete object from AWS S3',
            extra={'log_meta': orjson.dumps({'key': key, 'error': str(error)}).decode()},
        )
        raise self.retry(countdown=60)

    logger.info('Object successfully deleted from AWS S3', extra={'log_meta': orjson.dumps({'key': key}).decode()})

    return f'Object successfully deleted from AWS S3. Key: {key}'


@shared_task(bind=True, max_retries=10)
def abort_multipart_upload_task(self, key: str, upload_id: str) -> str:
    container: punq.Container = get_container()
    boto_provider: BaseBotoFileProvider = container.resolve(BaseBotoFileProvider)
    logger: Logger = container.resolve(Logger)

    try:
        logger.info(
            'Start aborting multipart upload from S3',
            extra={'log_meta': orjson.dumps({'key': key, 'upload_id': upload_id}).decode()},
        )
        boto_provider.abort_multipart_upload(
            key=key,
            upload_id=upload_id,
        )

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
        'Multipart upload successfully aborted from AWS S3',
        extra={'log_meta': orjson.dumps({'key': key, 'upload_id': upload_id}).decode()},
    )

    return 'Multipart upload successfully aborted from AWS S3. Key: {key}, Upload ID: {upload_id}'
