from dataclasses import dataclass

from core.apps.channels.services.s3_channels import BaseAvatarFilenameValidatorService
from core.apps.common.services.files import BaseS3FileService


# TODO: так как прямой PUT в S3 не возвращает KEY и BUCKET, то нужно сразу их сейвить при запрашивании URL?
# TODO: добавить получение аватарки
# TODO: Может быть закрыть бакет на публичный доступ, и выдавать только закрытый URL?


@dataclass
class GenerateUploadAvatarUrlUseCase:
    files_service: BaseS3FileService
    validator_service: BaseAvatarFilenameValidatorService

    def execute(self, filename: str) -> dict:
        self.validator_service.validate(filename=filename)

        url = self.files_service.generate_upload_url(
            filename=filename,
            expires_in=120,
            data_type='avatar',
        )

        return {'upload_url': url}
