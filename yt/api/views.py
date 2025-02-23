from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets
from .models import Channel, Video
from . import serializers
from .permissions import IsAuthenticatedOrAdminOrReadOnly
from rest_framework import permissions
from django.db.models import Count, Sum, Prefetch
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomUserViewSet(UserViewSet):
    """
    Customized UserViewSet from Djoser: prefetch_related('channel') has been added to queryset
    """

    queryset = get_user_model().objects.all().prefetch_related("channel")


class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for detail, update and delete instance.
    [!] If the request method is DELETE, related/associated user will also be deleted
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.method == "DELETE":
            return self.request.user

        return get_object_or_404(self.get_queryset(), user=self.request.user)


class ChannelMainView(generics.RetrieveAPIView):
    """
    API endpoint to get channel main page.
    Example: /api/v1/c/henwixchannel
    """

    queryset = Channel.objects.all().prefetch_related(
        Prefetch(
            "videos",
            Video.objects.filter(status=Video.VideoStatus.PUBLIC).annotate(views_count=Count("views")),
        )
    )
    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"


class ChannelAboutView(generics.RetrieveAPIView):
    """
    API endpoint to get info about channel.
    Example: /api/v1/c/henwixchannel/about/
    """

    queryset = (
        Channel.objects.all()
        .select_related("user")
        .prefetch_related("videos")
        .annotate(total_views=Count("videos__views"), total_videos=Count("videos"), total_subs=Count("followers"))
    )
    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"


class VideoViewSet(viewsets.ModelViewSet):
    # TODO: FILTERING & ORDERING
    """
    API endpoint for listing, retrieving, creating, editing and deleting Video instances.
    Supports searching by 'name', 'description', 'author__name', 'author__slug' fields.
    Returns nothing if 'search' query-param was not provided - ?search param for listing is required.
    """

    lookup_field = "video_id"
    lookup_url_kwarg = "video_id"
    permission_classes = [IsAuthenticatedOrAdminOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    pagination_class = CustomPageNumberPagination
    search_fields = ['@name', '@description', '@author__name', '@author__slug']
    ordering_fields = ['created_at', 'views_count']

    def get_serializer_class(self):
        """
        Custom get_serializer_class method.
        If action is list - return VideoPreviewSerializer else VideoSerializer
        """

        if self.action == 'list':
            return serializers.VideoPreviewSerializer
        return serializers.VideoSerializer

    def get_queryset(self):
        """
        Custom get_queryset method.

        """

        if self.action == 'list':
            if not self.request.query_params.get('search'):
                return []
            return (
                Video.objects.select_related("author")
                .filter(status=Video.VideoStatus.PUBLIC)
                .annotate(views_count=Count("views"))
            )
        if self.action == "retrieve":
            return (
                Video.objects.select_related("author")
                .all()
                .annotate(views_count=Count("views"), likes_count=Count("likes"))
            )
        return Video.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('search'):
            return Response(
                {'None': "No results found. Try different keywords or remove search filters"}
            )
        return super().list(request, *args, **kwargs)

