import pytest

from core.apps.videos.exceptions.upload import (
    VideoFilenameFormatError,
    VideoFilenameNotProvidedError,
)
from core.apps.videos.services.s3_videos import BaseVideoFilenameValidatorService


@pytest.mark.django_db
def test_video_filename_not_provided_error(video_filename_validator_service: BaseVideoFilenameValidatorService):
    """Test that an error has been raised when the video filename is not
    provided."""
    with pytest.raises(VideoFilenameNotProvidedError):
        video_filename_validator_service.validate(filename=None)


@pytest.mark.django_db
def test_video_filename_format_error(video_filename_validator_service: BaseVideoFilenameValidatorService):
    """Test that an error has been raised when the video filename format is
    incorrect."""
    with pytest.raises(VideoFilenameFormatError):
        video_filename_validator_service.validate(filename='test.txt')


@pytest.mark.django_db
@pytest.mark.parametrize('filename', ['test.mkv', 'test.mp4'])
def test_video_filename_format_correct(
    video_filename_validator_service: BaseVideoFilenameValidatorService,
    filename: str,
):
    """Test that the video filename format is correct."""
    video_filename_validator_service.validate(filename=filename)
