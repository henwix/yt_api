from core.apps.videos.providers.videos import BaseCeleryFileProvider


class CeleryFileProvider(BaseCeleryFileProvider):
    def delete_file(self, key: str) -> None:
        from core.apps.videos.tasks import delete_s3_video_task

        delete_s3_video_task.apply_async(
            args=(key,),
            queue='media-queue',
        )

    def delete_files(self, files: list) -> None:
        from core.apps.channels.tasks import delete_channel_files_task

        delete_channel_files_task.apply_async(
            args=(files,),
            queue='media-queue',
        )

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        from core.apps.videos.tasks import abort_multipart_upload_task

        abort_multipart_upload_task.apply_async(
            args=(key, upload_id),
            queue='media-queue',
        )
