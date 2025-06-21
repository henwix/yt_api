from core.apps.common.providers.files import BaseCeleryFileProvider
from core.project.celery import app


class CeleryFileProvider(BaseCeleryFileProvider):
    def delete_object_by_key(self, key: str, cache_key: str | None = None) -> None:
        app.send_task(
            'core.apps.common.tasks.delete_s3_object_task',
            args=(key, cache_key),
            queue='media-queue',
        )

    def delete_objects(self, objects: list[dict], cache_keys: list | None) -> None:
        app.send_task(
            'core.apps.common.tasks.delete_s3_objects_task',
            args=(objects, cache_keys),
            queue='media-queue',
        )

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        app.send_task(
            'core.apps.common.tasks.abort_multipart_upload_task',
            args=(key, upload_id),
            queue='media-queue',
        )
