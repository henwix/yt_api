import punq
import pytest

from core.apps.common.exceptions.captcha import (
    CaptchaTokenNotProvidedError,
    CaptchaValidationFailedError,
)
from core.apps.common.providers.captcha import BaseCaptchaProvider
from core.apps.common.services.captcha import (
    GoogleV2CaptchaService,
    GoogleV3CaptchaService,
)
from core.tests.mocks.captcha.captcha_provider import DummyCaptchaProvider


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [1, 0.9, 0.8, 0.7, 0.6])
def test_captcha_v3_token_validated_correctly(container: punq.Container, expected_score: int | float):
    """GoogleV3CaptchaService.

    Test that the captcha token is validated correctly if the score is
    greater than the minimum score in settings.

    """

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': expected_score},
        ),
    )
    service: GoogleV3CaptchaService = container.resolve('GoogleV3CaptchaService')

    result = service.validate_token(token='token', version='v3')

    assert result is True, f'{result=}'


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [0, 0.1, 0.2, 0.3, 0.4, 0.5])
def test_captcha_v3_token_validation_failed_score(container: punq.Container, expected_score: int | float):
    """GoogleV3CaptchaService.

    Test that an exception CaptchaValidationFailed raised when the score
    is less than the minimum score in in V3 Google Recaptcha service
    implementation.

    """

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': expected_score},
        ),
    )

    service: GoogleV3CaptchaService = container.resolve('GoogleV3CaptchaService')

    with pytest.raises(CaptchaValidationFailedError):
        service.validate_token(token='token', version='v3')


@pytest.mark.django_db
@pytest.mark.parametrize('expected_score', [0, 0.3, 0.6, 0.8, 1])
def test_captcha_v3_token_validation_failed_success(container: punq.Container, expected_score: int | float):
    """GoogleV3CaptchaService.

    Test that an exception CaptchaValidationFailed raised when the
    'success' field from Google API response is False.

    """

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': False, 'score': expected_score},
        ),
    )
    service: GoogleV3CaptchaService = container.resolve('GoogleV3CaptchaService')

    with pytest.raises(CaptchaValidationFailedError):
        service.validate_token(token='token', version='v3')


@pytest.mark.django_db
def test_captcha_v2_token_validation_failed_success(container: punq.Container):
    """GoogleV2CaptchaService.

    Test that an exception CaptchaValidationFailed raised when the
    'success' field from Google API response is False.

    """

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': False},
        ),
    )
    service: GoogleV2CaptchaService = container.resolve('GoogleV2CaptchaService')

    with pytest.raises(CaptchaValidationFailedError):
        service.validate_token(token='token', version='v2_visible')


@pytest.mark.django_db
def test_captcha_v2_token_not_provided(container: punq.Container):
    """Test that an exception CaptchaTokenNotProvidedError when the token is
    not provided."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True},
        ),
    )
    service: GoogleV2CaptchaService = container.resolve('GoogleV2CaptchaService')

    with pytest.raises(CaptchaTokenNotProvidedError):
        service.validate_token(token=None, version='v2_visible')


@pytest.mark.django_db
def test_captcha_v3_token_not_provided(container: punq.Container):
    """Test that an exception CaptchaTokenNotProvidedError when the token is
    not provided."""

    # register the mock captcha provider
    container.register(
        BaseCaptchaProvider, factory=lambda: DummyCaptchaProvider(
            response={'success': True, 'score': 1},
        ),
    )
    service: GoogleV3CaptchaService = container.resolve('GoogleV3CaptchaService')

    with pytest.raises(CaptchaTokenNotProvidedError):
        service.validate_token(token=None, version='v3')
