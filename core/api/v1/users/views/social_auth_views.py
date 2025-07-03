from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import SocialAuthBaseException
from social_django.utils import (
    load_backend,
    load_strategy,
)


class GenerateSocialAuthUrlView(APIView):
    def get(self, request, provider):
        redirect_uri = reverse_lazy('v1:users:social_auth', kwargs={'provider': provider})
        strategy = load_strategy(request)
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=redirect_uri)
        if not backend:
            return Response({'error': 'Invalid provider'}, status=400)

        #  Generate url(redirect_uri, state, scope, client_id in query-params) for auth
        auth_url = backend.auth_url()
        return Response({'auth_url': auth_url})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='code',
            description='Code parameter',
            required=True,
            type=str,
        ),
    ],
    summary='Social OAuth2. Return JWT tokens in response',
)
class SocialAuthWithCookieRedirectionView(APIView):
    def get(self, request, provider):
        try:
            # Load the strategy for the Django request
            strategy = load_strategy(request)

            # Load the backend for the specified provider
            backend: BaseOAuth2 = load_backend(
                strategy=strategy,
                name=provider,
                redirect_uri=reverse_lazy('v1:users:social_auth', kwargs={'provider': provider}),
            )

            user = backend.auth_complete(
                user=request.user if request.user.is_authenticated else None,
            )

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        tokens = {
            'refresh': str(refresh),
            'access': str(access),
        }

        return Response(data=tokens)
