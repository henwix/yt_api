import punq
import pytest

from core.apps.common.exceptions.captcha import (
    CaptchaTokenNotProvidedError,
    CaptchaValidationFailed,
)
from core.apps.common.providers.captcha import BaseCaptchaProvider
from core.apps.common.services.captcha import (
    BaseCaptchaService,
    GoogleV3CaptchaService,
)
from core.tests.mocks.captcha.captcha_provider import DummyCaptchaProvider


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [1, 0.9, 0.8, 0.7, 0.6])
def test_captcha_token_validated_correctly(container: punq.Container, expected_score: int | float):
    """Test that the captcha token is validated correctly if the score is
    greater than the minimum score in settings."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': expected_score},
        ),
    )
    service: BaseCaptchaService = container.resolve(BaseCaptchaService)

    result = service.validate_token(captcha_required=True, token='token')

    assert result is True, f'{result=}'


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [0, 0.1, 0.2, 0.3, 0.4, 0.5])
def test_captcha_v3_token_validation_failed_score(container: punq.Container, expected_score: int | float):
    """Test that an exception CaptchaValidationFailed raised when the score is
    less than the minimum score in in V3 Google Recaptcha service
    implementation."""

    # register the specific implementation for V3 token
    container.register(BaseCaptchaService, GoogleV3CaptchaService)

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': expected_score},
        ),
    )

    service: BaseCaptchaService = container.resolve(BaseCaptchaService)

    with pytest.raises(CaptchaValidationFailed):
        service.validate_token(captcha_required=True, token='token')


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [0, 0.3, 0.6, 0.8, 1])
def test_captcha_token_validation_failed_success(container: punq.Container, expected_score: int | float):
    """Test that an exception CaptchaValidationFailed raised when the 'success'
    field from Google API response is False."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': False, 'score': expected_score},
        ),
    )
    service: BaseCaptchaService = container.resolve(BaseCaptchaService)

    with pytest.raises(CaptchaValidationFailed):
        service.validate_token(captcha_required=True, token='token')


@pytest.mark.django_db
def test_captcha_token_not_provided(container: punq.Container):
    """Test that an exception CaptchaTokenNotProvidedError when the token is
    not provided."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': 1},
        ),
    )
    service: BaseCaptchaService = container.resolve(BaseCaptchaService)

    with pytest.raises(CaptchaTokenNotProvidedError):
        service.validate_token(captcha_required=True, token=None)


@pytest.mark.django_db
def test_captcha_token_not_required(container: punq.Container):
    """Test that the service returns True when the token is not required and
    not provided."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': 1},
        ),
    )
    service: BaseCaptchaService = container.resolve(BaseCaptchaService)

    result = service.validate_token(captcha_required=False, token=None)
    assert result is True, f'{result=}'
