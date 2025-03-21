from rest_framework import generics, viewsets

from .models import VideoReport
from .serializers import VideoReportSerializer


class VideoReportsView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView, viewsets.GenericViewSet):
    # TODO: fix error with DELETE button in listing endpoint at api/v1/video-reports/
    # TODO: add permissions and pagination

    serializer_class = VideoReportSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        if self.action in ['retrieve', 'list']:
            return VideoReport.objects.all().select_related('video', 'author')
        return VideoReport.objects.all()
