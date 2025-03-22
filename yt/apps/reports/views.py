from rest_framework import generics, viewsets

from apps.common.pagination import CustomCursorPagination

from .models import VideoReport
from .permissions import IsStaffOrCreateOnly
from .serializers import VideoReportSerializer


class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    serializer_class = VideoReportSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsStaffOrCreateOnly]

    def get_queryset(self):
        if self.action in ['retrieve', 'list']:
            return VideoReport.objects.all().select_related('video', 'author')
        return VideoReport.objects.all()
