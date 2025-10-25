from social_core.backends.oauth import BaseOAuth2PKCE
from social_core.exceptions import (
    AuthMissingParameter,
    AuthStateForbidden,
)
from social_core.utils import constant_time_compare

from core.apps.common.services.cache import BaseCacheService
from core.apps.users.exceptions.oauth2 import CustomAuthStateMissing
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
            self.cache_service.set(
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
        state = self.cache_service.get(
            key=f'oauth_state_{request_state}',
        )
        if not request_state:
            raise AuthMissingParameter(self, 'state')
        if not state:
            raise CustomAuthStateMissing(self, 'state')
        if not constant_time_compare(request_state, state):
            raise AuthStateForbidden(self)
        self.cache_service.delete(f'oauth_state_{request_state}')
        return state


class OAuth2PKCEMixin:
    """Custom mixin class that uses cache to save and retrieve 'code_verifier',
    instead of using session as it works in default OAuth2PKCE class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = get_container()
        self.cache_service: BaseCacheService = self.container.resolve(BaseCacheService)

    def create_code_verifier(self, state=None):
        """Takes a 'state' as a parameter to properly store the cache."""
        name = f'{self.name}_code_verifier'
        code_verifier_len = self.setting(
            'PKCE_CODE_VERIFIER_LENGTH',
            default=self.PKCE_DEFAULT_CODE_VERIFIER_LENGTH,
        )
        code_verifier = self.strategy.random_string(code_verifier_len)
        self.cache_service.set(f'{name}_{state}', code_verifier, 60 * 5)  # use cache
        return code_verifier

    def get_code_verifier(self, state=None):
        """Takes a 'state' as a parameter to properly retrieve the cache."""
        name = f'{self.name}_code_verifier'
        return self.cache_service.get(f'{name}_{state}')  # use cache

    def auth_params(self, state=None):
        """Custom method that adds a 'state' parameter to the
        'create_code_verifier' method call to make it works with the cache
        instead of using sessions.

        It also deliberately call super() with BaseOAuth2PKCE to invoke
        the auth_params method starting from the BaseOAuth2PKCE class in
        the MRO, not from the next class in the MRO. This ensures we
        execute only the required logic from BaseOAuth2PKCE, avoiding
        duplicate execution of logic that would occur if we used a
        regular super() call. Essentially, we copy the logic from the
        subsequent MRO class, but by specifying BaseOAuth2PKCE in
        super(), we prevent unnecessary duplication.

        """

        params = super(BaseOAuth2PKCE, self).auth_params(state=state)

        if self.setting('USE_PKCE', default=self.DEFAULT_USE_PKCE):
            code_challenge_method = self.setting(
                'PKCE_CODE_CHALLENGE_METHOD',
                default=self.PKCE_DEFAULT_CODE_CHALLENGE_METHOD,
            )
            code_verifier = self.create_code_verifier(state=state)  # pass the 'state' parameter
            code_challenge = self.generate_code_challenge(
                code_verifier,
                code_challenge_method,
            )
            params['code_challenge_method'] = code_challenge_method
            params['code_challenge'] = code_challenge
        return params

    def auth_complete_params(self, state=None):
        """Custom method that adds a 'state' parameter to the
        'get_code_verifier' method call to make it works with the cache instead
        of using sessions.

        It also deliberately call super() with BaseOAuth2PKCE to invoke
        the auth_complete_params method starting from the BaseOAuth2PKCE
        class in the MRO, not from the next class in the MRO. This
        ensures we execute only the required logic from BaseOAuth2PKCE,
        avoiding duplicate execution of logic that would occur if we
        used a regular super() call. Essentially, we copy the logic from
        the subsequent MRO class, but by specifying BaseOAuth2PKCE in
        super(), we prevent unnecessary duplication.

        """

        params = super(BaseOAuth2PKCE, self).auth_complete_params(state=state)

        if self.setting('USE_PKCE', default=self.DEFAULT_USE_PKCE):
            code_verifier = self.get_code_verifier(state=state)  # pass the 'state' parameter
            params['code_verifier'] = code_verifier

        return params
