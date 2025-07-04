from django.conf import settings
from django.urls import reverse_lazy
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import SocialAuthBaseException
from social_django.models import UserSocialAuth
from social_django.utils import (
    load_backend,
    load_strategy,
)

from core.apps.users.converters.users import user_to_entity
from core.apps.users.throttles import OAuth2ThrottleClass
from core.apps.users.use_cases.social_auth import SocialAuthUseCase
from core.project.containers import get_container


class GenerateSocialAuthUrlView(APIView):
    def get(self, request, provider):
        try:
            redirect_uri = reverse_lazy('v1:users:social-auth', kwargs={'provider': provider})
            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=redirect_uri)
            if not backend:
                return Response({'error': 'Invalid provider'}, status=400)

            #  Generate url(query-params depends on backend) for auth
            auth_url = backend.auth_url()

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

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
class SocialAuthVerifyView(APIView):
    throttle_classes = [OAuth2ThrottleClass]

    def get(self, request, provider):
        container = get_container()
        use_case: SocialAuthUseCase = container.resolve(SocialAuthUseCase)

        try:
            # Load strategy and backend for the specified provider
            backend: BaseOAuth2 = load_backend(
                strategy=load_strategy(request),
                name=provider,
                redirect_uri=reverse_lazy('v1:users:social-auth', kwargs={'provider': provider}),
            )
            # Complete Social OAuth and retrieve or create user
            user = backend.auth_complete(
                user=request.user if request.user.is_authenticated else None,
            )

            # create a new channel if not exists and return JWT tokens
            result = use_case.execute(user=user_to_entity(user))

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        return Response(data=result)


class SocialAuthDisconnectView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, provider):
        try:
            backend: BaseOAuth2 = load_backend(
                strategy=load_strategy(request),
                name=provider,
                redirect_uri=reverse_lazy('v1:users:social-auth', kwargs={'provider': provider}),
            )

            backend.disconnect(user=request.user)

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        return Response({'status': f'{provider} successfully disconnected'})


class SocialAuthConnectedList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_backends = UserSocialAuth.objects.filter(user=request.user)
        names = [i.provider for i in user_backends]
        response = {}
        for i in settings.OAUTH2_ALLOWED_BACKENDS.keys():
            response[i] = True if i in names else False

        return Response({'connected': response})
