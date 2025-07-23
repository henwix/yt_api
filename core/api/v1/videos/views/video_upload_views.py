from logging import Logger

from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import orjson
import punq
from botocore.exceptions import ClientError
from drf_spectacular.utils import extend_schema

from core.api.v1.common.serializers.upload_serializers import (
    AbortUploadSerializer,
    CompleteUploadSerializer,
    GenerateUploadPartUrlSerializer,
    KeySerializer,
)
from core.api.v1.videos.serializers import video_serializers
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.use_cases.videos_upload.abort_upload_video import AbortVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.complete_upload_video import CompleteVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.create_upload_video import CreateVideoMultipartUploadUseCase
from core.apps.videos.use_cases.videos_upload.download_video_url import GenerateUrlForVideoDownloadUseCase
from core.apps.videos.use_cases.videos_upload.upload_video_url import GenerateUrlForVideoUploadUseCase
from core.project.containers import get_container


@extend_schema(
    responses={
        201: {
            'type': 'object',
            'properties': {
                'upload_id': {
                    'type': 'string',
                    'example': 'test_upload_id',
                },
                'key': {
                    'type': 'string',
                    'example': 'videos/test_key.mp4',
                },
            },
        },
    },
    summary='Create multipart upload',
)
class CreateMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = video_serializers.VideoCreateSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CreateVideoMultipartUploadUseCase = container.resolve(CreateVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                filename=serializer.validated_data.pop('filename'),
                validated_data=serializer.validated_data,
            )

        except ClientError as error:
            logger.error(
                "S3 client can't create multipart upload",
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
                'upload_url': {
                    'type': 'string',
                    'example': 'test_upload_url',
                },
            },
        },
    },
    summary='Generate upload url for video',
)
class GenerateUploadPartUrlView(generics.GenericAPIView):
    serializer_class = GenerateUploadPartUrlSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForVideoUploadUseCase = container.resolve(GenerateUrlForVideoUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                part_number=serializer.validated_data.get('part_number'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video upload",
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
                    'description': 'Presigned URL for video download',
                },
            },
        },
    },
    summary='Generate presigned url for video download',
)
class GenerateDownloadVideoUrlView(generics.GenericAPIView):
    serializer_class = KeySerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForVideoDownloadUseCase = container.resolve(GenerateUrlForVideoDownloadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video download",
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
    summary='Abort multipart upload',
)
class AbortMultipartUploadView(generics.GenericAPIView):
    serializer_class = AbortUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: AbortVideoMultipartUploadUseCase = container.resolve(AbortVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't abort multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'error': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
                'message': {
                    'type': 'string',
                    'example': 'Video upload completed successfully',
                },
            },
        },
    },
    summary='Complete multipart upload',
)
class CompleteMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteUploadSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteVideoMultipartUploadUseCase = container.resolve(CompleteVideoMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                parts=serializer.validated_data.get('parts'),
            )

        except ClientError as error:
            logger.error(
                "S3 client can't complete multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'error': error.response.get('Error', {}).get('Message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)
