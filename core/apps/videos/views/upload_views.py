from logging import Logger

from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
from botocore.exceptions import ClientError
from drf_spectacular.utils import extend_schema

from core.apps.common.exceptions import ServiceException
from core.apps.videos.serializers import video_serializers
from core.apps.videos.serializers.video_upload_serializers import (
    AbortUploadSerializer,
    CompleteUploadSerializer,
    GenerateUploadPartUrlSerializer,
)
from core.apps.videos.services.videos import BaseVideoPresignedURLService
from core.apps.videos.use_cases.multipart_upload.abort_upload import AbortMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.complete_upload import CompleteUploadUseCase
from core.apps.videos.use_cases.multipart_upload.initiate_upload import InitiateMultipartUploadUseCase
from core.apps.videos.use_cases.multipart_upload.presigned_url_upload import GenerateUrlForUploadUseCase
from core.project.containers import get_container


class GeneratePresignedUrlView(APIView):
    """API endpoint to generate presigned URL for channel_avatar uploading to
    S3.

    Takes one required parameter: 'filename' to generate URL based on that name.
    Example: /api/v1/get-upload-link/17388dff.jpg/

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoPresignedURLService = container.resolve(BaseVideoPresignedURLService)

    def get(self, request, filename):
        #  TODO: add try except to s3 errors
        result = self.service.generate_url(filename=filename)
        return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'status': {'type': 'string'},
                'filename': {'type': 'string'},
            },
            'required': ['name', 'filename'],
        },
    },
)
class InitiateMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = video_serializers.VideoSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: InitiateMultipartUploadUseCase = container.resolve(InitiateMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()

        try:
            result = use_case.execute(
                user=request.user,
                filename=request.data.get('filename'),
                validated_data=serializer.validated_data,
            )
        except ClientError as error:
            logger.error(
                "S3 client can't create multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


class GenerateUploadPartUrlView(generics.GenericAPIView):
    serializer_class = GenerateUploadPartUrlSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: GenerateUrlForUploadUseCase = container.resolve(GenerateUrlForUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                part_number=serializer.validated_data.get('part_number'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't generate presigned url for video upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_201_CREATED)


class AbortMultipartUploadView(generics.GenericAPIView):
    serializer_class = AbortUploadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        container: punq.Container = get_container()
        use_case: AbortMultipartUploadUseCase = container.resolve(AbortMultipartUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't abort multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)


class CompleteMultipartUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteUploadSerializer

    def post(self, request):
        container: punq.Container = get_container()
        use_case: CompleteUploadUseCase = container.resolve(CompleteUploadUseCase)
        logger: Logger = container.resolve(Logger)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=request.user,
                key=serializer.validated_data.get('key'),
                upload_id=serializer.validated_data.get('upload_id'),
                parts=serializer.validated_data.get('parts'),
            )
        except ClientError as error:
            logger.error(
                "S3 client can't complete multipart upload",
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response({'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK)
