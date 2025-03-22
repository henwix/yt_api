import logging
import os
from datetime import timedelta

import boto3
import django_filters
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from apps.common.pagination import CustomCursorPagination
from apps.common.permissions import (
    IsAuthenticatedOrAdminOrReadOnly,
    IsAuthenticatedOrAuthorOrReadOnly,
)

from . import serializers
from .filters import VideoFilter
from .models import Playlist, PlaylistItem, Video, VideoComment, VideoHistory, VideoLike, VideoView
from .pagination import HistoryCurstorPagination
from .permissions import IsAuthorOrReadOnlyPlaylist

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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]
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

    @action(url_path='like', methods=['post', 'delete'], detail=True)
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

        if request.method == 'POST':
            is_like = request.data.get('is_like', True)

            like, created = VideoLike.objects.get_or_create(
                channel=channel,
                video=video,
                defaults={
                    'is_like': is_like,
                },
            )

            if not created:
                like.is_like = is_like
                like.save()

            return Response({'status': 'success', 'is_like': is_like}, status=HTTP_200_OK)

        if request.method == 'DELETE':
            deleted, _ = VideoLike.objects.filter(channel=channel, video=video).delete()

            if deleted:
                return Response({'status': 'Success'}, status=HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Like not found'}, HTTP_404_NOT_FOUND)

    @action(url_path='view', methods=['post'], detail=True)
    def view(self, request, video_id):
        """
        API endpoint for adding views to videos.

        Have no required fields.
        Allows add a view if the previous one was more than 24 hours ago.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/view/
        """

        channel = getattr(request.user, 'channel', None)
        video = get_object_or_404(Video, video_id=video_id)
        ip_address = request.META.get('REMOTE_ADDR')

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
            return Response({'status': 'success'}, status=HTTP_201_CREATED)
        else:
            return Response({'error': 'View already exists'}, status=HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        """
        Custom 'get_serializer_class' method.
        If action is list - return VideoPreviewSerializer else VideoSerializer
        """

        if self.action == 'list':
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
                return []
            return (
                Video.objects.select_related('author')
                .filter(status=Video.VideoStatus.PUBLIC)
                .annotate(views_count=Count('views', distinct=True))
            )
        if self.action == 'retrieve':
            return (
                Video.objects.select_related('author')
                .all()
                .annotate(
                    views_count=Count('views', distinct=True),
                    likes_count=Count('likes', filter=Q(likes__is_like=True), distinct=True),
                    comments_count=Count('comments'),
                    subs_count=Count('author__followers', distinct=True),
                )
            )
        return Video.objects.all()

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
            return Response({'error': 'Unsupported file format'}, status=HTTP_400_BAD_REQUEST)

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

        return Response({'put_url': url}, status=HTTP_200_OK)


class VideoHistoryView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint to get list of wathed videos.
    Supports cursor pagonation.
    Example: api/v1/history/
    """

    lookup_field = 'video_id'
    permission_classes = [IsAuthenticated]
    pagination_class = HistoryCurstorPagination
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
                {'error': 'To add video in history you need to provide his video_id'}, status=HTTP_400_BAD_REQUEST
            )

        try:
            history_item, created = VideoHistory.objects.get_or_create(channel=request.user.channel, video_id=video_id)
        except IntegrityError:
            return Response({'error': 'Video does not exists'})

        if not created:
            history_item.watched_at = timezone.now()
            history_item.save(update_fields=['watched_at'])
            return Response({'status': 'Success: Updated previous history item'}, status=HTTP_200_OK)

        return Response({'status': 'Success: Created new history item'}, status=HTTP_201_CREATED)

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
            return Response({'status': 'Video successfully deleted from history'}, status=HTTP_204_NO_CONTENT)

        return Response({'error': 'Video does not exists or never been in history'}, status=HTTP_404_NOT_FOUND)


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

    # FIXME: check requests in silk and add pagination

    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthorOrReadOnlyPlaylist]

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
    @action(methods=['post'], url_name='add-video', url_path='add-video', detail=True)
    def add_video_in_playlist(self, request, id):
        """
        API endpoint to add video in playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /api/v1/playlists/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/add-video/?v=33CjPuGJsEZ
        """

        if not id:
            return Response({'error': 'To add video you need to provide playlist id'}, status=HTTP_400_BAD_REQUEST)

        video_id = request.query_params.get('v')

        if not video_id:
            return Response(
                {'error': 'To add video in that playlist you need to provide video_id'}, status=HTTP_400_BAD_REQUEST
            )

        playlist_item, created = PlaylistItem.objects.get_or_create(playlist_id=id, video_id=video_id)
        if created:
            return Response({'status': 'Video added in playlist'}, status=HTTP_200_OK)
        return Response({'status': 'Video already exists in that playlist'}, status=HTTP_200_OK)

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
    @action(methods=['delete'], url_name='delete-video', url_path='delete-video', detail=True)
    def delete_video_from_playlist(self, request, id):
        """
        API endpoint to delete video from playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /api/v1/playlists/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/delete-video/?v=33CjPuGJsEZ
        """

        if not id:
            return Response({'error': 'To delete video you need to provide playlist id'}, status=HTTP_400_BAD_REQUEST)

        video_id = request.query_params.get('v')

        if not video_id:
            return Response(
                {'error': 'To delete video in that playlist you need to provide video_id'}, status=HTTP_400_BAD_REQUEST
            )

        deleted, _ = PlaylistItem.objects.filter(playlist_id=id, video_id=video_id).delete()

        if deleted:
            return Response({'status': 'Video successfully deleted from playlist'}, status=HTTP_204_NO_CONTENT)
        return Response({'status': 'Video does not exists in that playlist'}, status=HTTP_400_BAD_REQUEST)
