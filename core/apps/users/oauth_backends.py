from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.exceptions import (
    AuthMissingParameter,
    AuthStateForbidden,
)
from social_core.utils import constant_time_compare

from core.apps.common.services.cache import BaseCacheService
from core.apps.users.exceptions.social_auth import CustomAuthStateMissing
from core.project.containers import get_container


class OAuth2Mixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = get_container()
        self.cache_service: BaseCacheService = self.container.resolve(BaseCacheService)

    def get_or_create_state(self):
        """Generate a state token for OAuth2 authentication and save it in the
        cache for 5 minutes."""
        if self.STATE_PARAMETER or self.REDIRECT_STATE:
            state = self.state_token()
            self.cache_service.cache_data(
                key=f'oauth_state_{state}',
                data=state,
                timeout=60 * 5,
            )
        else:
            state = None
        return state

    def validate_state(self):
        """Validate the state parameter for OAuth2 authentication.

        This method checks if the state parameter is present in the
        request, retrieves the cached state from the cache service, and
        compares it with the request state. If they do not match, it
        raises an exception.

        If the state is valid, it deletes the cached state from the
        cache service.

        """
        if not self.STATE_PARAMETER and not self.REDIRECT_STATE:
            return None
        request_state = self.get_request_state()
        state = self.cache_service.get_cached_data(
            key=f'oauth_state_{request_state}',
        )
        if not request_state:
            raise AuthMissingParameter(self, "state")
        if not state:
            raise CustomAuthStateMissing(self, "state")
        if not constant_time_compare(request_state, state):
            raise AuthStateForbidden(self)
        self.cache_service.delete_cached_data(f'oauth_state_{request_state}')
        return state


class CustomGoogleOAuth2(OAuth2Mixin, GoogleOAuth2):
    """Custom Google OAuth2 backend with custom state handling via cache."""
    STATE_PARAMETER = True


class CustomGitHubOAuth2(OAuth2Mixin, GithubOAuth2):
    """Custom GitHub OAuth2 backend with custom state handling via cache."""
    STATE_PARAMETER = True
