from logging import Logger

from rest_framework import (
    generics,
    status,
    viewsets,
)
from rest_framework.response import Response

import orjson
import punq
from drf_spectacular.utils import extend_schema

from core.api.v1.reports.serializers import VideoReportSerializer
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.pagination import CustomCursorPagination
from core.apps.reports.permissions import IsStaffOrCreateOnly
from core.apps.reports.services.reports import BaseVideoReportsService
from core.apps.reports.use_cases.create import CreateReportUseCase
from core.apps.users.converters.users import user_to_entity
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

    @extend_schema(
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'successfully created',
                    },
                },
            },
        },
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
