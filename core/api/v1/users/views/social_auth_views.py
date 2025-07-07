from django.urls import reverse_lazy
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import punq
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import SocialAuthBaseException
from social_django.utils import (
    load_backend,
    load_strategy,
)

from core.apps.users.converters.users import user_to_entity
from core.apps.users.throttles import OAuth2ThrottleClass  # noqa
from core.apps.users.use_cases.oauth2_complete import OAuth2CompleteUseCase
from core.apps.users.use_cases.oauth2_connected_providers import OAuth2ConnectedProvidersUseCase
from core.project.containers import get_container


@extend_schema(summary='Get the provider and return the generated link for OAuth2.')
class OAuth2GenerateUrlView(APIView):
    # throttle_classes = [OAuth2ThrottleClass]

    def get(self, request, provider):
        try:
            redirect_uri = reverse_lazy('v1:users:social-auth', kwargs={'provider': provider})
            backend = load_backend(
                strategy=load_strategy(request),
                name=provider,
                redirect_uri=redirect_uri,
            )
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
        OpenApiParameter(
            name='state',
            description='State parameter',
            required=True,
            type=str,
        ),
    ],
    summary='Verify SocialOAuth2 data and return JWT tokens as a response if the user is not authorized',
)
class OAuth2ConnectView(APIView):
    # throttle_classes = [OAuth2ThrottleClass]

    def get(self, request, provider):
        container = get_container()
        use_case: OAuth2CompleteUseCase = container.resolve(OAuth2CompleteUseCase)
        request_user = request.user

        try:
            # Load strategy and backend for the specified provider
            backend: BaseOAuth2 = load_backend(
                strategy=load_strategy(request),
                name=provider,
                redirect_uri=reverse_lazy('v1:users:social-auth', kwargs={'provider': provider}),
            )
            # Complete Social OAuth and retrieve or create user
            retrieved_user = backend.auth_complete(
                user=request_user if request_user.is_authenticated else None,
            )

            # Create a new channel if doesn't exists and return JWT tokens if the user is not authenticated
            result = use_case.execute(
                retrieved_user=user_to_entity(retrieved_user),
                provider=provider,
                is_authenticated=request_user.is_authenticated,
            )

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        return Response(data=result)


@extend_schema(summary='Disconnect OAuth2 provider')
class OAuth2DisconnectView(APIView):
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


@extend_schema(summary='Retrieve connected OAuth2 providers')
class OAuth2ConnectedProvidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        container: punq.Container = get_container()
        use_case: OAuth2ConnectedProvidersUseCase = container.resolve(OAuth2ConnectedProvidersUseCase)

        result = use_case.execute(user=user_to_entity(request.user))
        return Response(data=result)
