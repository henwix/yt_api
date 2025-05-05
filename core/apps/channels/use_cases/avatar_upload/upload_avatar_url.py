from dataclasses import dataclass

from core.apps.channels.services.s3_channels import BaseAvatarFilenameValidatorService
from core.apps.common.services.files import BaseS3FileService


@dataclass
class GenerateUploadAvatarUrlUseCase:
    files_service: BaseS3FileService
    validator_service: BaseAvatarFilenameValidatorService

    def execute(self, filename: str) -> dict:
        self.validator_service.validate(filename=filename)

        url, key = self.files_service.generate_upload_url(
            filename=filename,
            expires_in=120,
            data_type='avatar',
        )

        return {'upload_url': url, 'key': key}
