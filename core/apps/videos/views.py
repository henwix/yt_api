import logging
import os

import boto3
import django_filters
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.apps.common.pagination import CustomCursorPagination, CustomPageNumberPagination
from core.apps.common.permissions import (
    IsAuthenticatedOrAdminOrReadOnly,
    IsAuthenticatedOrAuthorOrReadOnly,
)
from core.project.containers import get_container

from . import serializers
from .filters import VideoFilter
from .models import Playlist, PlaylistItem, Video, VideoComment, VideoHistory
from .pagination import HistoryCursorPagination
from .permissions import IsAuthorOrReadOnlyPlaylist
from .services.videos import BaseVideoService

log = logging.getLogger(__name__)


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing, retrieving, creating, editing and deleting 'Video' instances.
    Supports searching by 'name', 'description', 'author__name', 'author__slug' fields.
    Returns nothing if 'search' query-param was not provided - '?search' param for listing is required.
    Example: api/v1/video?search=airplane
    """

    lookup_field = 'video_id'
    lookup_url_kwarg = 'video_id'
    permission_classes = [IsAuthenticatedOrAdminOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filterset_class = VideoFilter
    pagination_class = CustomCursorPagination
    search_fields = ['@name', '@description', '@author__name', '@author__slug']
    ordering_fields = ['created_at', 'views_count']
    throttle_scope = 'video'

    # TODO: доделать multipart upload
    # def create(self, request, *args, **kwargs):
    #     file = request.data.pop('file')

    #     if not file:
    #         return Response("File field cannot be blank!")

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid()
    #     self.perform_create(serializer)

    #     return super().create(request, *args, **kwargs)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseVideoService = container.resolve(BaseVideoService)

    @action(url_path='like', methods=['post'], detail=True)
    def like_create(self, request, video_id):
        """
        API endpoint to create like or dislike.

        Only one field can be provided: 'is_like' - true by default and means like, but false - dislike.
        Video determines by 'video_id' URL-parameter.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/like/
        """
        result = self.service.like_create(request.user, video_id, request.data.get('is_like', True))

        return Response(result, status.HTTP_201_CREATED)

    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, video_id):
        """
        API endpoint to delete like or dislike.

        No parameters required.
        Video determines by 'video_id' URL-parameter.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/unlike/
        """
        result = self.service.like_delete(request.user, video_id)

        return Response(result, status.HTTP_204_NO_CONTENT)

    @action(url_path='view', methods=['post'], detail=True)
    def view_create(self, request, video_id):
        """
        API endpoint for adding views to videos.

        Have no required fields.
        Allows add a view if the previous one was more than 24 hours ago.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/view/
        """
        result = self.service.view_create(
            user=request.user,
            video_id=video_id,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        return Response(result, status.HTTP_201_CREATED)

    def get_serializer_class(self):
        """
        Custom 'get_serializer_class' method.

        If action is list - return VideoPreviewSerializer else VideoSerializer
        """
        if action == 'list':
            return serializers.VideoPreviewSerializer
        return serializers.VideoSerializer

    def get_queryset(self):
        """
        Custom get_queryset method.

        Add 'views_count' annotated field if action == 'list' for 'Video' preview.

        If action == 'retrieve' - add views_count and likes_count for 'Video' detail info.
        """
        if self.action == 'list':
            if not self.request.query_params.get('search'):
                return Video.objects.none()

            return self.service.get_videos_for_listing()

        if self.action == 'retrieve':
            return self.service.get_videos_for_retrieve()

        return self.service.get_all_videos()

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('search'):
            return Response({'None': 'No results found. Try different keywords or remove search filters'})
        return super().list(request, *args, **kwargs)


class CommentVideoAPIView(viewsets.ModelViewSet):
    """
    API endpoint for listing, retrieving, updating and deleting Video Comments.

    Permissions:
        GET - Everyone
        POST - Authenticated only
        DELETE/POST/PUT - Comment's author only

    Supports pagination by cursor.

    Example: /api/v1/video-comment/?v=uN9qVyjTrO6
    """

    serializer_class = serializers.VideoCommentSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            video = self.request.query_params.get('v')
            if not video:
                return []
            return VideoComment.objects.all().select_related('author', 'video').filter(video__video_id=video)
        return VideoComment.objects.all().select_related('author', 'video')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description="Parameter identifying video to get related video's comment",
                required=True,
                type=str,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        if not request.query_params.get('v'):
            return Response({'None': 'No comments found.'})
        return super().list(request, *args, **kwargs)


class GeneratePresignedUrlView(APIView):
    """
    API endpoint to generate presigned URL for channel_avatar uploading to S3.
    Takes one required parameter: 'filename' to generate URL based on that name.
    Example: /api/v1/get-upload-link/17388dff.jpg/
    """

    def get(self, request, filename):
        if filename and filename[-4:] not in ['.png', '.jpg']:
            return Response(
                {'error': 'Unsupported file format'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME'),
        )

        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
                'Key': f'channel_avatars/{filename}',
            },
            ExpiresIn=120,
            HttpMethod='PUT',
        )

        return Response({'put_url': url}, status=status.HTTP_200_OK)


class VideoHistoryView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint to get list of watched videos.
    Supports cursor pagination.
    Example: api/v1/history/
    """

    lookup_field = 'video_id'
    permission_classes = [IsAuthenticated]
    pagination_class = HistoryCursorPagination
    serializer_class = serializers.VideoHistorySerializer

    def get_queryset(self):
        if self.action == 'delete':
            return VideoHistory.objects.filter(channel=self.request.user.channel)
        return VideoHistory.objects.filter(channel=self.request.user.channel).select_related('video__author')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to add in playlist.',
                required=True,
                type=str,
            )
        ]
    )
    @action(methods=['post'], detail=False, url_path='add', url_name='add')
    def add_video_in_history(self, request):
        """
        API endpoint to add video in watching history.
        To add video you need to provide required query parameter - 'v' with video_id.
        Example: api/v1/history/add/?v=au90D2BoHuT
        """

        video_id = request.query_params.get('v')

        if not video_id:
            return Response(
                {'error': 'To add video in history you need to provide his video_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            history_item, created = VideoHistory.objects.get_or_create(channel=request.user.channel, video_id=video_id)
        except IntegrityError:
            return Response({'error': 'Video does not exists'})

        if not created:
            history_item.watched_at = timezone.now()
            history_item.save(update_fields=['watched_at'])
            return Response(
                {'status': 'Success: Updated previous history item'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {'status': 'Success: Created new history item'},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to delete from history.',
                required=True,
                type=str,
            )
        ]
    )
    @action(methods=['delete'], url_path='delete', url_name='delete', detail=False)
    def delete_video_from_history(self, request):
        """
        API endpoint to delete video from watching history.

        To delete video you need to provide required query parameter - 'v' with video_id.

        Example: api/v1/history/delete/?v=au90D2BoHuT
        """

        video_id = request.query_params.get('v')

        if not video_id:
            return Response({'error': 'To delete video from history you need to provide his video_id'})

        deleted, _ = VideoHistory.objects.filter(channel=request.user.channel, video_id=video_id).delete()

        if deleted:
            return Response(
                {'status': 'Video successfully deleted from history'},
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(
            {'error': 'Video does not exists or never been in history'},
            status=status.HTTP_404_NOT_FOUND,
        )


class MyVideoView(generics.ListAPIView):
    """
    API endpoint to get all user's videos.

    Supports cursor pagination.

    Example: api/v1/my-videos/
    """

    serializer_class = serializers.VideoPreviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        return Video.objects.all().filter(author=self.request.user.channel).select_related('author')


class PlaylistAPIView(viewsets.ModelViewSet):
    """
    API endpoint to list/retrieve/create/update/delete playlists.

    Permissions and access:
    - create: authenticated only
    - list: authenticated only
    - retrieve: allow any if not private
    - delete and update: author or staff only

    Example: api/v1/playlists/, api/v1/playlists/kn2puLWEDmqIvavBgvYRSypsb162jSHE/
    """

    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthorOrReadOnlyPlaylist]
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PlaylistPreviewSerializer
        return serializers.PlaylistSerializer

    def get_queryset(self):
        if self.action == 'list':
            return (
                Playlist.objects.filter(channel=self.request.user.channel)
                .prefetch_related('videos__author')
                .select_related('channel')
                .annotate(videos_count=Count('videos', distinct=True))
            )
        if self.action == 'retrieve':
            return (
                Playlist.objects.prefetch_related('videos__author')
                .select_related('channel')
                .annotate(videos_count=Count('videos', distinct=True))
            )
        return Playlist.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to add to playlist.',
                required=True,
                type=str,
            )
        ]
    )
    @action(
        methods=['post'],
        url_name='add-video',
        url_path='add-video',
        detail=True,
    )
    def add_video_in_playlist(self, request, id):
        """
        API endpoint to add video in playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /api/v1/playlists/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/add-video/?v=33CjPuGJsEZ
        """

        if not id:
            return Response(
                {'error': 'To add video you need to provide playlist id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_id = request.query_params.get('v')

        if not video_id:
            return Response(
                {'error': 'To add video in that playlist you need to provide video_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        playlist_item, created = PlaylistItem.objects.get_or_create(playlist_id=id, video_id=video_id)
        if created:
            return Response({'status': 'Video added in playlist'}, status=status.HTTP_200_OK)
        return Response(
            {'status': 'Video already exists in that playlist'},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to delete from playlist.',
                required=True,
                type=str,
            )
        ]
    )
    @action(
        methods=['delete'],
        url_name='delete-video',
        url_path='delete-video',
        detail=True,
    )
    def delete_video_from_playlist(self, request, id):
        """
        API endpoint to delete video from playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /api/v1/playlists/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/delete-video/?v=33CjPuGJsEZ
        """

        if not id:
            return Response(
                {'error': 'To delete video you need to provide playlist id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_id = request.query_params.get('v')

        if not video_id:
            return Response(
                {'error': 'To delete video in that playlist you need to provide video_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = PlaylistItem.objects.filter(playlist_id=id, video_id=video_id).delete()

        if deleted:
            return Response(
                {'status': 'Video successfully deleted from playlist'},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {'status': 'Video does not exists in that playlist'},
            status=status.HTTP_400_BAD_REQUEST,
        )
