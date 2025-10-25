from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2
from social_core.backends.twitter_oauth2 import TwitterOAuth2

from core.apps.users.oauth2_backends_mixins import (
    OAuth2Mixin,
    OAuth2PKCEMixin,
)


class CustomGoogleOAuth2(OAuth2Mixin, GoogleOAuth2):
    """Custom Google OAuth2 backend with custom state handling via cache."""

    STATE_PARAMETER = True


class CustomGitHubOAuth2(OAuth2Mixin, GithubOAuth2):
    """Custom GitHub OAuth2 backend with custom state handling via cache."""

    STATE_PARAMETER = True


class CustomTwitterOAuth2(OAuth2PKCEMixin, OAuth2Mixin, TwitterOAuth2):
    """Custom Twitter/X OAuth2 backend with updated methods."""

    STATE_PARAMETER = True
    DEFAULT_USE_PKCE = True
    DEFAULT_SCOPE = ['users.read', 'users.email', 'tweet.read']

    def get_user_details(self, response):
        """Custom method that extracts user details from a Twitter/X
        account/response.

        The 'response' field contains a dictionary with user details as
        a response from the resource server.

        """
        return {
            'id': response['id'],
            'username': response['username'],
            'email': response['confirmed_email'],
        }

    def user_data(self, access_token, *args, **kwargs):
        """Custom method that make a request to Twitter/X resource server using
        'access_token" to retrieve a user data.

        Here we change the list of user fields:
            - remove unused ones
            - leave only those field that we will use and add a new one with user's email
        https://docs.x.com/x-api/users/user-lookup-me

        """
        fields = [
            'id',
            'username',
            'confirmed_email',
        ]
        response = self.get_json(
            'https://api.twitter.com/2/users/me',
            params={'user.fields': ','.join(fields)},
            headers={'Authorization': f'Bearer {access_token}'},
        )
        return response['data']
