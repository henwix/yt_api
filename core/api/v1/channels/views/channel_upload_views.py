from logging import Logger

from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.response import Response

import orjson
import punq
from botocore.exceptions import ClientError
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
)

from core.api.v1.common.serializers.upload_serializers import (
    FilenameSerializer,
    KeySerializer,
)
from core.apps.channels.use_cases.avatar_upload.complete_upload_avatar import CompleteUploadAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.delete_avatar import DeleteChannelAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.download_avatar_url import GenerateUrlForAvatarDownloadUseCase
from core.apps.channels.use_cases.avatar_upload.upload_avatar_url import GenerateUploadAvatarUrlUseCase
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'filename': {'type': 'string', 'example': 'avatar.jpg'},
            },
            'required': ['filename'],
        },
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'upload_url': {
                    'type': 'string',
                },
                'key': {
                    'type': 'string',
                },
            },
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                    'example': 'Unsupported avatar file format',
                },
            },
        },
        500: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                },
            },
        },
    },
    summary='Generate presigned url for avatar upload',
)
class GenerateUploadAvatarUrlView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FilenameSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUploadAvatarUrlUseCase = container.resolve(GenerateUploadAvatarUrlUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(filename=serializer.validated_data.get('filename'))

        except ClientError as error:
            logger.error(
                "S3 client can't generate upload avatar url",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'error': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        201: {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                },
            },
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                    'example': 'File with this key does not exist in S3',
                },
            },
        },
        500: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                },
            },
        },
    },
    summary='Generate presigned url for avatar download',
)
class GenerateDownloadAvatarUrlView(generics.GenericAPIView):
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForAvatarDownloadUseCase = container.resolve(GenerateUrlForAvatarDownloadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                key=serializer.validated_data.get('key'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for avatar download",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'error': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                },
            },
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                },
            },
        },
    },
    examples=[
        OpenApiExample(
            name='Avatar deleted',
            value={'status': 'success'},
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            name='Channel not found',
            value={'error': 'Channel not found'},
            response_only=True,
            status_codes=[404],
        ),
        OpenApiExample(
            name='Avatar does not exists',
            value={'error': 'Avatar does not exists'},
            response_only=True,
            status_codes=[404],
        ),
    ],
    summary='Delete channel avatar',
)
class DeleteChannelAvatarView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        container: punq.Container = get_container()
        use_case: DeleteChannelAvatarUseCase = container.resolve(DeleteChannelAvatarUseCase)
        logger: Logger = container.resolve(Logger)

        try:
            result = use_case.execute(user=user_to_entity(request.user))

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                },
            },
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                },
            },
        },
        500: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                },
            },
        },
    },
    examples=[
        OpenApiExample(
            name='Avatar deleted',
            value={'status': 'success'},
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            name='Channel not found',
            value={'error': 'Channel not found'},
            response_only=True,
            status_codes=[404],
        ),
        OpenApiExample(
            name='File does not exists',
            value={'error': 'File with this key does not exist in S3'},
            response_only=True,
            status_codes=[404],
        ),
    ],
    summary='Complete avatar uploading',
)
class CompleteUploadAvatarView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteUploadAvatarUseCase = container.resolve(CompleteUploadAvatarUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                key=serializer.validated_data.get('key'),
                user=user_to_entity(request.user),
            )

        except ServiceException as error:
            logger.error(
                error.message,
                extra={'log_meta': orjson.dumps(error).decode()},
            )
            raise

        return Response(result, status=status.HTTP_200_OK)
