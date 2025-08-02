from logging import Logger

from rest_framework import (
    filters,
    generics,
    mixins,
    serializers as drf_serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import django_filters
import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from core.api.v1.common.serializers.comments import (
    CommentIdParameterSerializer,
    CommentLikeSerializer,
)
from core.api.v1.common.serializers.serializers import (
    LikeCreateInSerializer,
    LikeCreateOutSerializer,
)
from core.api.v1.videos.serializers.history import VideoHistorySerializer
from core.api.v1.videos.serializers.video_serializers import (
    CommentCreatedSerializer,
    PlaylistPreviewSerializer,
    PlaylistSerializer,
    UpdatePlaylistSerializer,
    VideoCommentSerializer,
    VideoPreviewSerializer,
    VideoSerializer,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.mixins import CustomViewMixin
from core.apps.common.pagination import (
    CustomCursorPagination,
    CustomPageNumberPagination,
)
from core.apps.common.permissions import IsAuthenticatedOrAuthorOrReadOnly
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.converters.videos import video_to_entity
from core.apps.videos.filters import VideoFilter
from core.apps.videos.models import Video
from core.apps.videos.pagination import HistoryCursorPagination
from core.apps.videos.permissions import (
    IsAuthorOrReadOnlyPlaylist,
    VideoIsAuthenticatedOrAuthorOrAdminOrReadOnly,
)
from core.apps.videos.services.comments import BaseVideoCommentService
from core.apps.videos.services.videos import (
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoService,
)
from core.apps.videos.signals import video_pre_delete
from core.apps.videos.use_cases.comments.comment_create import CreateVideoCommentUseCase
from core.apps.videos.use_cases.comments.get_comments_list import GetVideoCommentsUseCase
from core.apps.videos.use_cases.comments.like_create import VideoCommentLikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import VideoCommentLikeDeleteUseCase
from core.apps.videos.use_cases.history.clear_history import ClearVideoHistoryUseCase
from core.project.containers import get_container


class VideoViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
):
    """API endpoint for listing, retrieving, creating, editing and deleting
    'Video' instances.

    Supports searching by 'name', 'description', 'author__name', 'author__slug' fields.
    Returns nothing if 'search' query-param was not provided - '?search' param for listing is required.
    Example: /v1/video?search=airplane

    """

    lookup_field = 'video_id'
    lookup_url_kwarg = 'video_id'
    permission_classes = [VideoIsAuthenticatedOrAuthorOrAdminOrReadOnly]
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoService = container.resolve(BaseVideoService)
        self.logger: Logger = container.resolve(Logger)

    @extend_schema(
        request=LikeCreateInSerializer,
        responses=LikeCreateOutSerializer,
        summary='Like or dislike video',
    )
    @action(url_path='like', methods=['post'], detail=True)
    def like_create(self, request, video_id):
        """API endpoint to create like or dislike.

        Only one field can be provided: 'is_like' - true by default and means like, but false - dislike.
        Video determines by 'video_id' URL-parameter.

        """
        try:
            result = self.service.like_create(
                user=user_to_entity(request.user),
                video_id=video_id,
                is_like=request.data.get('is_like', True),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        video_pre_delete.send(sender=Video, instance=instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='VideoLikeDeleted',
                    fields={
                        'status': drf_serializers.CharField(),
                    },
                ),
                description="Like deleted",
                examples=[
                    OpenApiExample(
                        name="Deleted",
                        value={
                            "status": "success",
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        summary='Delete like or dislike for video',
    )
    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, video_id):
        """API endpoint to delete like or dislike.

        No parameters required. Video determines by 'video_id' URL-
        parameter.

        """
        try:
            result = self.service.like_delete(user=user_to_entity(request.user), video_id=video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name='View Created',
                    fields={
                        'status': drf_serializers.CharField(),
                    },
                ),
                description="View created",
                examples=[
                    OpenApiExample(
                        name="Created",
                        value={
                            "status": "success",
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        summary='Add view to video',
    )
    @action(url_path='view', methods=['post'], detail=True)
    def view_create(self, request, video_id):
        """API endpoint for adding views to videos.

        Have no required fields. Allows add a view if the previous one
        was more than 24 hours ago.

        """
        try:
            result = self.service.view_create(
                user=user_to_entity(request.user),
                video_id=video_id,
                ip_address=request.META.get('HTTP_X_REAL_IP'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    def get_serializer_class(self):
        """Custom 'get_serializer_class' method.

        If action is list - return VideoPreviewSerializer else VideoSerializer

        """
        if self.action == 'list':
            return VideoPreviewSerializer
        return VideoSerializer

    def get_queryset(self):
        """Custom get_queryset method.

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


class CommentVideoAPIView(viewsets.ModelViewSet, CustomViewMixin):
    serializer_class = VideoCommentSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count', 'replies_count']
    ordering = ['-likes_count']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.service: BaseVideoCommentService = self.container.resolve(BaseVideoCommentService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_queryset(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return self.service.get_annotated_queryset()
        return self.service.get_related_queryset()

    @extend_schema(responses=CommentCreatedSerializer)
    def create(self, request, *args, **kwargs):
        use_case: CreateVideoCommentUseCase = self.container.resolve(CreateVideoCommentUseCase)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                video=video_to_entity(serializer.validated_data.get('video')),
                text=serializer.validated_data.get('text'),
                reply_comment_id=getattr(serializer.validated_data.get('reply_comment'), 'pk', None),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        return Response(CommentCreatedSerializer(result).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description="Parameter identifying video to get related video's comment",
                required=True,
                type=str,
            ),
        ],
        summary="Get video's comments",
    )
    def list(self, request, *args, **kwargs):
        use_case: GetVideoCommentsUseCase = self.container.resolve(GetVideoCommentsUseCase)

        try:
            qs = use_case.execute(
                user=user_to_entity(request.user),
                video_id=request.query_params.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filtration_and_pagination(qs)
        return result

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.service.change_updated_status(comment_id=kwargs.get('pk'), is_updated=True)
        return response

    @extend_schema(summary="Get comment's replies")
    @action(url_path='replies', url_name='replies', detail=True)
    def get_replies_list(self, request, pk):
        serializer = CommentIdParameterSerializer(data={'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            qs = self.service.get_replies_by_comment_id(comment_id=pk)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filtration_and_pagination(qs)
        return result

    @extend_schema(
        request=LikeCreateInSerializer,
        responses=LikeCreateOutSerializer,
        summary='Create like or dislike for comment',
    )
    @action(methods=['post'], url_path='like', detail=True)
    def like_create(self, request, pk):
        use_case: VideoCommentLikeCreateUseCase = self.container.resolve(VideoCommentLikeCreateUseCase)
        is_like = request.data.get('is_like', True)

        serializer = CommentLikeSerializer(data={'is_like': is_like, 'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                comment_id=pk,
                is_like=is_like,
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='VideoCommentLikeDeleted',
                    fields={
                        'status': drf_serializers.CharField(),
                    },
                ),
                description="Like deleted",
                examples=[
                    OpenApiExample(
                        name="Deleted",
                        value={
                            "status": "success",
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        summary='Delete like or dislike for comment',
    )
    @action(methods=['delete'], url_path='unlike', detail=True)
    def like_delete(self, request, pk):
        use_case: VideoCommentLikeDeleteUseCase = self.container.resolve(VideoCommentLikeDeleteUseCase)

        serializer = CommentLikeSerializer(data={'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                comment_id=pk,
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)


class VideoHistoryView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to get list of watched videos.

    Supports cursor pagination.
    Example: /v1/history/

    """

    lookup_field = 'video_id'
    permission_classes = [IsAuthenticated]
    pagination_class = HistoryCursorPagination
    serializer_class = VideoHistorySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.service: BaseVideoHistoryService = self.container.resolve(BaseVideoHistoryService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_queryset(self):
        if self.action == 'delete':
            return self.service.get_channel_history(user=user_to_entity(self.request.user))
        return self.service.get_history_for_retrieve(user=user_to_entity(self.request.user))

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                    },
                },
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                    },
                },
            },
        },
        examples=[
            OpenApiExample(
                name='History cleared',
                value={'status': 'history cleared'},
                response_only=True,
                status_codes=[200],
            ),
            OpenApiExample(
                name='History is empty',
                value={'error': 'history is empty'},
                response_only=True,
                status_codes=[400],
            ),
        ],
        summary='Clear video history',
    )
    @action(methods=['delete'], detail=False, url_path='clear')
    def clear_history(self, request):
        use_case: ClearVideoHistoryUseCase = self.container.resolve(ClearVideoHistoryUseCase)

        try:
            deleted, result = use_case.execute(
                user=user_to_entity(request.user),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status=status.HTTP_200_OK if deleted else status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to add in playlist.',
                required=True,
                type=str,
            ),
        ],
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'Video added in history',
                    },
                },
            },
        },
        summary='Add video in history',
    )
    @action(methods=['post'], detail=False, url_path='add', url_name='add')
    def add_video_in_history(self, request):
        video_id = request.query_params.get('v')

        try:
            result = self.service.add_video_in_history(
                user=user_to_entity(request.user),
                video_id=video_id,
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to delete from history.',
                required=True,
                type=str,
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'Video successfully deleted from history',
                    },
                },
            },
        },
        summary='Delete video from history',
    )
    @action(methods=['delete'], url_path='delete', url_name='delete', detail=False)
    def delete_video_from_history(self, request):
        try:
            result = self.service.delete_video_from_history(
                user=user_to_entity(request.user),
                video_id=request.query_params.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)


@extend_schema(summary='Get all personal channel videos')
class MyVideoView(generics.ListAPIView):
    serializer_class = VideoPreviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        return Video.objects.all().filter(author=self.request.user.channel).select_related('author')


#  TODO: maybe remove 'videos' from serializer and add new endpoints to load all playlist's related videos
class PlaylistAPIView(viewsets.ModelViewSet):
    """API endpoint to list/retrieve/create/update/delete playlists.

    Permissions and access:
    - create: authenticated only
    - list: authenticated only
    - retrieve: allow any if not private
    - delete and update: author or staff only

    """

    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthorOrReadOnlyPlaylist]
    pagination_class = CustomPageNumberPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoPlaylistService = container.resolve(BaseVideoPlaylistService)
        self.logger: Logger = container.resolve(Logger)

    def get_serializer_class(self):
        if self.action == 'list':
            return PlaylistPreviewSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return UpdatePlaylistSerializer
        return PlaylistSerializer

    def get_queryset(self):
        if self.action == 'list':
            return self.service.get_playlists_for_listing(user_to_entity(self.request.user))
        return self.service.get_playlists_for_retrieving()

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to add to playlist.',
                required=True,
                type=str,
            ),
        ],
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'Video added in playlist',
                    },
                },
            },
        },
        summary='Add video in playlist',
    )
    @action(
        methods=['post'],
        url_name='add-video',
        url_path='add-video',
        detail=True,
    )
    def add_video_in_playlist(self, request, id):
        """API endpoint to add video in playlist.

        Requires 'playlist id' in URL and 'v' query param which contains
        video_id.

        """
        try:
            result = self.service.add_video_in_playlist(
                playlist_id=id,
                video_id=request.query_params.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to delete from playlist.',
                required=True,
                type=str,
            ),
        ],
        summary='Delete video from playlist',
    )
    @action(
        methods=['delete'],
        url_name='delete-video',
        url_path='delete-video',
        detail=True,
    )
    def delete_video_from_playlist(self, request, id):
        """API endpoint to delete video from playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /v1/playlist/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/delete-video/?v=33CjPuGJsEZ

        """
        try:
            result = self.service.delete_video_from_playlist(
                playlist_id=id,
                video_id=request.query_params.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)
