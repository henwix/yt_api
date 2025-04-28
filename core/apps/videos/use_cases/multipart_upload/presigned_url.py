from dataclasses import dataclass

from core.apps.videos.services.upload import (
    BaseUploadIdValidatorService,
    BaseUploadKeyValidatorService,
)
from core.apps.videos.services.videos import BaseMultipartUploadVideoService


@dataclass
class GenerateUrlForUploadUseCase:
    upload_service: BaseMultipartUploadVideoService
    upload_id_validator_service: BaseUploadIdValidatorService
    upload_key_validator_service: BaseUploadKeyValidatorService

    def execute(self, key: str, upload_id: str, part_number: int) -> str:
        self.upload_key_validator_service.validate(key=key)
        self.upload_id_validator_service.validate(upload_id=upload_id)

        url = self.upload_service.generate_upload_part_url(
            key=key,
            upload_id=upload_id,
            part_number=part_number,
        )

        return {'upload_url': url}
