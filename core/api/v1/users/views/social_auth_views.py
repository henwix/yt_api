from logging import Logger

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from social_core.exceptions import SocialAuthBaseException
from social_django.utils import load_strategy

from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
from core.apps.users.throttles import OAuth2ThrottleClass  # noqa
from core.apps.users.use_cases.oauth2_connect import OAuth2ConnectUseCase
from core.apps.users.use_cases.oauth2_connected_providers import OAuth2ConnectedProvidersUseCase
from core.apps.users.use_cases.oauth2_disconnect import OAuth2DisconnectUseCase
from core.apps.users.use_cases.oauth2_generate_url import OAuth2GenerateURLUseCase
from core.project.containers import get_container


@extend_schema(summary='Generate URL for OAuth2 authorization')
class OAuth2GenerateURLView(APIView):
    throttle_classes = [OAuth2ThrottleClass]

    def get(self, request, provider):
        container: punq.Container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: OAuth2GenerateURLUseCase = container.resolve(OAuth2GenerateURLUseCase)

        try:
            result = use_case.execute(
                strategy=load_strategy(request),
                provider=provider,
            )

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response({'auth_url': result})


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
    summary='Verify SocialOAuth2 data and connect service to user',
)
class OAuth2ConnectView(APIView):
    throttle_classes = [OAuth2ThrottleClass]

    def get(self, request, provider):
        container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: OAuth2ConnectUseCase = container.resolve(OAuth2ConnectUseCase)

        try:
            result = use_case.execute(
                strategy=load_strategy(request),
                user=request.user,
                provider=provider,
            )

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data=result)


@extend_schema(summary='Disconnect OAuth2 provider')
class OAuth2DisconnectView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, provider):
        container: punq.Container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: OAuth2DisconnectUseCase = container.resolve(OAuth2DisconnectUseCase)

        try:
            result = use_case.execute(
                user=request.user,
                strategy=load_strategy(request),
                provider=provider,
            )

        except SocialAuthBaseException as e:
            return Response({'error': str(e)}, status=400)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data=result)


@extend_schema(summary='Retrieve connected OAuth2 providers')
class OAuth2ConnectedProvidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        container: punq.Container = get_container()
        use_case: OAuth2ConnectedProvidersUseCase = container.resolve(OAuth2ConnectedProvidersUseCase)

        result = use_case.execute(user=user_to_entity(request.user))
        return Response(data=result)
