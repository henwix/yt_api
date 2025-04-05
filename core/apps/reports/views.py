from rest_framework import (
    generics,
    status,
    viewsets,
)
from rest_framework.response import Response

from core.apps.common.pagination import CustomCursorPagination
from core.project.containers import get_container

from .permissions import IsStaffOrCreateOnly
from .serializers import VideoReportSerializer
from .services.reports import BaseVideoReportsService


class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseVideoReportsService = container.resolve(BaseVideoReportsService)

    def get_queryset(self):
        if self.action == ['list', 'retrieve']:
            return self.service.get_report_list_related()
        return self.service.get_report_list()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = self.service.create_report(
            video_id=request.data.get('video'),
            user=request.user,
            reason=request.data.get('reason'),
            description=request.data.get('description'),
        )

        return Response(result, status.HTTP_201_CREATED)
