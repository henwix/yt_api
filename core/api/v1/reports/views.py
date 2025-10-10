from logging import Logger

from rest_framework import (
    generics,
    status,
    viewsets,
)
from rest_framework.response import Response

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from core.api.v1.common.serializers.serializers import DetailOutSerializer
from core.api.v1.reports.serializers import VideoReportSerializer
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    created_response_example,
)
from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomCursorPagination
from core.apps.reports.exceptions.reports import ReportLimitError
from core.apps.reports.permissions import IsStaffOrCreateOnly
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.reports.use_cases.create import CreateReportUseCase
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.exceptions.videos import (
    PrivateVideoOrUploadingError,
    VideoNotFoundByVideoIdError,
)
from core.project.containers import get_container


class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.service: BaseVideoReportsService = self.container.resolve(BaseVideoReportsService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_queryset(self):
        if self.action == ['list', 'retrieve']:
            return self.service.get_report_list_related()
        return self.service.get_report_list()

    @extend_schema(summary='Get list of video reports')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary='Retrieve video report')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary='Delete video report')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        responses={
            201: OpenApiResponse(response=DetailOutSerializer, description='Video report has been created'),
            400: OpenApiResponse(response=DetailOutSerializer, description='Limit of reports has been reached'),
            403: OpenApiResponse(response=DetailOutSerializer, description='Video access denied'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video or channel was not found'),
        },
        examples=[
            created_response_example(),
            build_example_response_from_error(error=ReportLimitError),
            build_example_response_from_error(error=PrivateVideoOrUploadingError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
            build_example_response_from_error(error=ChannelNotFoundError),
        ],
        summary='Create a new video report',
    )
    def create(self, request, *args, **kwargs):
        use_case: CreateReportUseCase = self.container.resolve(CreateReportUseCase)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                video_id=serializer.validated_data.get('video_slug').pk,
                reason=serializer.validated_data.get('reason'),
                description=serializer.validated_data.get('description'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        else:
            return Response(result, status.HTTP_201_CREATED)
