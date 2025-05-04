from core.apps.common.providers.files import BaseCeleryFileProvider


class CeleryFileProvider(BaseCeleryFileProvider):
    def delete_object_by_key(self, key: str) -> None:
        from core.apps.common.tasks import delete_s3_object_task

        delete_s3_object_task.apply_async(
            args=(key,),
            queue='media-queue',
        )

    def delete_objects(self, objects: list[dict]) -> None:
        from core.apps.common.tasks import delete_s3_objects_task

        delete_s3_objects_task.apply_async(
            args=(objects,),
            queue='media-queue',
        )

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        from core.apps.common.tasks import abort_multipart_upload_task

        abort_multipart_upload_task.apply_async(
            args=(key, upload_id),
            queue='media-queue',
        )
