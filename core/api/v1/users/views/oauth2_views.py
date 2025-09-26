from logging import Logger

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    PolymorphicProxySerializer,
)
from social_core.exceptions import SocialAuthBaseException
from social_django.utils import load_strategy

from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    JWTOutSerializer,
)
from core.api.v1.schema.response_examples.common import (
    detail_response_example,
    error_response_example,
    jwt_response_example,
)
from core.api.v1.schema.response_examples.oauth2 import (
    oauth2_connected_providers_response_example,
    social_auth_error_response_example,
)
from core.api.v1.users.serializers.oauth2 import (
    AuthUrlSerializer,
    OAuth2ConnectedProvidersSerializer,
    OAuth2ConnectSerializer,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
from core.apps.users.errors import (
    ErrorCodes as UsersErrorCodes,
    ERRORS as USERS_ERRORS,
)
from core.apps.users.throttles import OAuth2ThrottleClass  # noqa
from core.apps.users.use_cases.oauth2.oauth2_connect import OAuth2ConnectUseCase
from core.apps.users.use_cases.oauth2.oauth2_connected_providers import OAuth2ConnectedProvidersUseCase
from core.apps.users.use_cases.oauth2.oauth2_disconnect import OAuth2DisconnectUseCase
from core.apps.users.use_cases.oauth2.oauth2_generate_url import OAuth2GenerateURLUseCase
from core.project.containers import get_container


@extend_schema(
    responses={
        201: AuthUrlSerializer,
        400: DetailOutSerializer,
    },
    examples=[
        error_response_example(USERS_ERRORS[UsersErrorCodes.OAUTH2_PROVIDER_NOT_SUPPORTED]),
        social_auth_error_response_example(),
    ],
    summary='Generate URL for OAuth2 authorization',
)
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

        except SocialAuthBaseException as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response({'auth_url': result})


@extend_schema(
    parameters=[OAuth2ConnectSerializer],
    responses={
        200: PolymorphicProxySerializer(
            component_name='OAuth2ConnectResponse',
            serializers=[JWTOutSerializer, DetailOutSerializer],
            resource_type_field_name=None,
        ),
        400: DetailOutSerializer,
    },
    examples=[
        jwt_response_example(),
        detail_response_example(
            name='Connected',
            value='github successfully connected',
            status_code=200,
        ),
        error_response_example(USERS_ERRORS[UsersErrorCodes.OAUTH2_PROVIDER_NOT_SUPPORTED]),
        social_auth_error_response_example(),
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

        except SocialAuthBaseException as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data=result)


@extend_schema(
    responses={
        200: DetailOutSerializer,
        400: DetailOutSerializer,
    },
    examples=[
        detail_response_example(
            name='Disconnected',
            value='github successfully disconnected',
            status_code=200,
        ),
        error_response_example(USERS_ERRORS[UsersErrorCodes.OAUTH2_PROVIDER_NOT_SUPPORTED]),
        social_auth_error_response_example(),
    ],
    summary='Disconnect OAuth2 provider',
)
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

        except SocialAuthBaseException as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data=result)


@extend_schema(
    responses={
        200: OAuth2ConnectedProvidersSerializer,
    },
    examples=[oauth2_connected_providers_response_example()],
    summary='Retrieve connected OAuth2 providers',
)
class OAuth2ConnectedProvidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        container: punq.Container = get_container()
        use_case: OAuth2ConnectedProvidersUseCase = container.resolve(OAuth2ConnectedProvidersUseCase)

        result = use_case.execute(user=user_to_entity(request.user))
        return Response(data=result)
