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
from drf_spectacular.utils import extend_schema

from core.apps.channels.use_cases.avatar_upload.complete_upload_avatar import CompleteUploadAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.delete_avatar import DeleteChannelAvatarUseCase
from core.apps.channels.use_cases.avatar_upload.download_avatar_url import GenerateUrlForAvatarDownloadUseCase
from core.apps.channels.use_cases.avatar_upload.upload_avatar_url import GenerateUploadAvatarUrlUseCase
from core.apps.common.exceptions import ServiceException
from core.apps.common.serializers.upload_serializers import KeySerializer
from core.project.containers import get_container


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'filename': {'type': 'string'},
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
    },
    summary='Generate presigned url for avatar upload',
)
class GenerateUploadAvatarUrlView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUploadAvatarUrlUseCase = container.resolve(GenerateUploadAvatarUrlUseCase)
        logger: Logger = container.resolve(Logger)

        try:
            result = use_case.execute(filename=request.data.get('filename'))

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
                    'example': 'success',
                },
            },
        },
    },
    summary='Delete channel avatar',
)
class DeleteChannelAvatarView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        container: punq.Container = get_container()
        use_case: DeleteChannelAvatarUseCase = container.resolve(DeleteChannelAvatarUseCase)
        logger: Logger = container.resolve(Logger)

        try:
            result = use_case.execute(user=request.user)

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
                    'example': 'success',
                },
            },
        },
    },
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
            result = use_case.execute(key=serializer.validated_data.get('key'), user=request.user)

        except ServiceException as error:
            logger.error(
                error.message,
                extra={'log_meta': orjson.dumps(error).decode()},
            )
            raise

        return Response(result, status=status.HTTP_200_OK)
