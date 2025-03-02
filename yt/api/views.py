from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets
from .models import Channel, Video, VideoLike, VideoView, VideoComment
from . import serializers
from .permissions import IsAuthenticatedOrAdminOrReadOnly
from rest_framework import permissions
from django.db.models import Count, Prefetch, Subquery, OuterRef, IntegerField, Q
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_204_NO_CONTENT,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
)
from rest_framework.pagination import PageNumberPagination, CursorPagination
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class CustomCursorPagination(CursorPagination):
    page_size = 2
    page_size_query_param = "page_size"
    ordering = "created_at"
    max_page_size = 50


class CustomUserViewSet(UserViewSet):
    """
    Customized UserViewSet from Djoser.
    prefetch_related('channel') has been added to queryset
    """

    queryset = get_user_model().objects.all().prefetch_related("channel")


class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for detail, update and delete 'Channel' instances.
    If the request method is DELETE, related/associated 'User' will also be deleted.
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.method == "DELETE":
            return self.request.user

        return get_object_or_404(self.get_queryset(), user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with caching.
        """
        
        cache_key = f"retrieve_channel_{self.request.user.pk}"

        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)
        
        response = super().retrieve(request, *args, **kwargs)
        cache.set(
            key=cache_key,
            value=response.data,
            timeout=60*15
        )
        return response

class ChannelMainView(generics.RetrieveAPIView):
    """
    API endpoint to get channel main page. Main page includes info about channel and last public 5 videos.
    Example: /api/v1/c/henwixchannel
    """

    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"
    throttle_scope = 'channel'

    def get_queryset(self):
        second_query = (
            Video.objects.select_related("author")
            .filter(author__slug=OuterRef("author__slug"), status=Video.VideoStatus.PUBLIC)
            .values("pk")[:5]
        )

        queryset = Channel.objects.all().prefetch_related(
            Prefetch("videos", Video.objects.filter(pk__in=Subquery(second_query)).annotate(views_count=Count("views")))
        )
        return queryset


class ChannelAboutView(generics.RetrieveAPIView):
    """
    API endpoint to get info about channel.
    Supports caching. Cache available in 15 minutes.
    Example: /api/v1/c/henwixchannel/about/
    """

    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            Channel.objects.all()
            .select_related("user")
            .annotate(
                total_views=Count("videos__views"),
                total_videos=Count("videos", filter=Q(videos__status=Video.VideoStatus.PUBLIC), distinct=True),
                total_subs=Count("followers"),
            )
        )
        return queryset
    
    @method_decorator(cache_page(60*15, key_prefix="channel_about"))
    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with @cache_page decorator caching.
        """

        return super().retrieve(request, *args, **kwargs)


class VideoViewSet(viewsets.ModelViewSet):
    # TODO: FILTERING & ORDERING
    """
    API endpoint for listing, retrieving, creating, editing and deleting 'Video' instances.
    Supports searching by 'name', 'description', 'author__name', 'author__slug' fields.
    Returns nothing if 'search' query-param was not provided - '?search' param for listing is required.
    Example: api/v1/video?search=airplane
    """

    lookup_field = "video_id"
    lookup_url_kwarg = "video_id"
    permission_classes = [IsAuthenticatedOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomCursorPagination
    search_fields = ["@name", "@description", "@author__name", "@author__slug"]
    ordering_fields = ["created_at", "views_count"]
    throttle_scope = 'video'

    @action(url_path="like", methods=["post", "delete"], detail=True)
    def like(self, request, video_id):
        """
        API endpoint for 'likes' and 'dislikes' actions.
        'POST' and 'DELETE' methods are available for setting 'likes'/'dislikes' and removing them.
        
        POST: Only one field can be provided: 'is_like' - true by default and means like, but false - dislike.
        DELETE: Have no required fields.
        Related video determines by 'video_id' query-param.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/like/
        """

        channel = request.user.channel
        video = get_object_or_404(Video, video_id=video_id)

        if request.method == "POST":
            is_like = request.data.get("is_like", True)

            like, created = VideoLike.objects.get_or_create(
                channel=channel,
                video=video,
                defaults={
                    "is_like": is_like,
                },
            )

            if not created:
                like.is_like = is_like
                like.save()

            return Response({"status": "success", "is_like": is_like}, status=HTTP_200_OK)

        if request.method == "DELETE":
            deleted, _ = VideoLike.objects.filter(channel=channel, video=video).delete()

            if deleted:
                return Response({"status": "Success"}, status=HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Like not found"}, HTTP_404_NOT_FOUND)

    @action(url_path="view", methods=["post"], detail=True)
    def view(self, request, video_id):
        """
        API endpoint for adding views to videos.
        
        Have no required fields.
        Allows add a view if the previous one was more than 24 hours ago.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/view/
        """

        channel = getattr(request.user, "channel", None)
        video = get_object_or_404(Video, video_id=video_id)
        ip_address = request.META.get("REMOTE_ADDR")

        last_view = VideoView.objects.filter(
            channel=channel if channel else None,
            ip_address=ip_address if ip_address else None,
            video=video,
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()

        if not last_view:
            VideoView.objects.create(
                channel=channel,
                video=video,
                ip_address=ip_address,
            )
            return Response({"status": "success"}, status=HTTP_201_CREATED)
        else:
            return Response({"error": "View already exists"}, status=HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        """
        Custom 'get_serializer_class' method.
        If action is list - return VideoPreviewSerializer else VideoSerializer
        """

        if self.action == "list":
            return serializers.VideoPreviewSerializer
        return serializers.VideoSerializer

    def get_queryset(self):
        """
        Custom get_queryset method.

        Add 'views_count' annotated field if action == 'list' for 'Video' preview.
        If action == 'retrieve' - add views_count and likes_count for 'Video' detail info.
        """

        if self.action == "list":
            if not self.request.query_params.get("search"):
                return []
            return (
                Video.objects.select_related("author")
                .filter(status=Video.VideoStatus.PUBLIC)
                .annotate(views_count=Count("views"))
            )
        if self.action == "retrieve":

            second_query = VideoLike.objects.filter(
                is_like=True,
                video__video_id=OuterRef('video_id')
            ).values('video').annotate(count=Count('pk')).values('count')

            return (
                Video.objects.select_related("author")
                .all()
                .annotate(
                    views_count=Count("views"),
                    likes_count=Subquery(second_query, output_field=IntegerField()),
                )
            )
        return Video.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.query_params.get("search"):
            return Response({"None": "No results found. Try different keywords or remove search filters"})
        return super().list(request, *args, **kwargs)

class CommentAPIView(viewsets.ModelViewSet):
    # create
    # update
    # delete
    # list

    queryset = VideoComment.objects.all().select_related('author')
    serializer_class = serializers.VideoCommentSerializer
    # permission_classes = [IsAuthenticatedOrAuthor]

