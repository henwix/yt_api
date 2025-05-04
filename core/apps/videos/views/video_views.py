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

from core.apps.common.exceptions import ServiceException
from core.apps.common.mixins import PaginationMixin
from core.apps.common.pagination import (
    CustomCursorPagination,
    CustomPageNumberPagination,
)
from core.apps.common.permissions import (
    IsAuthenticatedOrAdminOrReadOnly,
    IsAuthenticatedOrAuthorOrReadOnly,
)
from core.apps.videos.filters import VideoFilter
from core.apps.videos.models import (
    Video,
    VideoHistory,
)
from core.apps.videos.pagination import HistoryCursorPagination
from core.apps.videos.permissions import IsAuthorOrReadOnlyPlaylist
from core.apps.videos.serializers import video_serializers
from core.apps.videos.services.comments import BaseCommentService
from core.apps.videos.services.videos import (
    BaseVideoHistoryService,
    BaseVideoPlaylistService,
    BaseVideoService,
)
from core.apps.videos.use_cases.comments.like_create import CommentLikeCreateUseCase
from core.apps.videos.use_cases.comments.like_delete import CommentLikeDeleteUseCase
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoService = container.resolve(BaseVideoService)
        self.logger: Logger = container.resolve(Logger)

    @extend_schema(
        request=inline_serializer(
            name='VideoLikeCreate',
            fields={
                'is_like': drf_serializers.BooleanField(required=False),
            },
        ),
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name='VideoLikeCreated',
                    fields={
                        'status': drf_serializers.CharField(),
                        'is_like': drf_serializers.BooleanField(),
                    },
                ),
                description="Like created",
                examples=[
                    OpenApiExample(
                        name="Like: True",
                        value={
                            "status": "success",
                            "is_like": True,
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        name="Like: False",
                        value={
                            "status": "success",
                            "is_like": False,
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    @action(url_path='like', methods=['post'], detail=True)
    def like_create(self, request, video_id):
        """API endpoint to create like or dislike.

        Only one field can be provided: 'is_like' - true by default and means like, but false - dislike.
        Video determines by 'video_id' URL-parameter.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/like/

        """
        try:
            result = self.service.like_create(request.user, video_id, request.data.get('is_like', True))
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, video_id):
        """API endpoint to delete like or dislike.

        No parameters required.
        Video determines by 'video_id' URL-parameter.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/unlike/

        """
        try:
            result = self.service.like_delete(request.user, video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None)
    @action(url_path='view', methods=['post'], detail=True)
    def view_create(self, request, video_id):
        """API endpoint for adding views to videos.

        Have no required fields.
        Allows add a view if the previous one was more than 24 hours ago.

        Example: http://127.0.0.1:8001/api/v1/video/JDcWD0w9aJD/view/

        """
        try:
            result = self.service.view_create(
                user=request.user,
                video_id=video_id,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    def get_serializer_class(self):
        """Custom 'get_serializer_class' method.

        If action is list - return VideoPreviewSerializer else VideoSerializer

        """
        if action == 'list':
            return video_serializers.VideoPreviewSerializer
        return video_serializers.VideoSerializer

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


class CommentVideoAPIView(viewsets.ModelViewSet, PaginationMixin):
    """API endpoint for listing, retrieving, updating and deleting Video
    Comments.

    Permissions:
        GET - Everyone
        POST - Authenticated only
        DELETE/POST/PUT - Comment's author only

    Supports pagination by cursor.

    Example: /api/v1/videos-comment/?v=uN9qVyjTrO6

    """

    serializer_class = video_serializers.VideoCommentSerializer
    pagination_class = CustomCursorPagination
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-likes_count']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.service: BaseCommentService = self.container.resolve(BaseCommentService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_queryset(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return self.service.repository.get_all_comments()
        return self.service.get_related_queryset()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description="Parameter identifying video to get related video's comment",
                required=True,
                type=str,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        try:
            qs = self.service.get_comments_by_video_id(
                video_id=request.query_params.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filter_and_pagination(qs)
        return result

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.service.change_updated_status(comment_id=kwargs.get('pk'))
        return response

    @action(url_path='replies', url_name='replies', detail=True)
    def get_replies_list(self, request, pk):
        try:
            qs = self.service.get_replies_by_comment_id(comment_id=pk)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filter_and_pagination(qs)
        return result

    @extend_schema(
        request=inline_serializer(
            name='VideoCommentLikeCreate',
            fields={
                'is_like': drf_serializers.BooleanField(required=False),
            },
        ),
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name='CommentLikeCreate',
                    fields={
                        'status': drf_serializers.CharField(),
                        'is_like': drf_serializers.BooleanField(),
                    },
                ),
                description="Like created",
                examples=[
                    OpenApiExample(
                        name="Like: True",
                        value={
                            "status": "success",
                            "is_like": True,
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        name="Like: False",
                        value={
                            "status": "success",
                            "is_like": False,
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    @action(methods=['post'], url_path='like', detail=True)
    def like_create(self, request, pk):
        use_case: CommentLikeCreateUseCase = self.container.resolve(CommentLikeCreateUseCase)

        try:
            result = use_case.execute(
                user=request.user,
                comment_id=pk,
                is_like=request.data.get('is_like', True),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @action(methods=['delete'], url_path='unlike', detail=True)
    def like_delete(self, request, pk):
        use_case: CommentLikeDeleteUseCase = self.container.resolve(CommentLikeDeleteUseCase)

        try:
            result = use_case.execute(
                user=request.user,
                comment_id=pk,
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_204_NO_CONTENT)


class VideoHistoryView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to get list of watched videos.

    Supports cursor pagination.
    Example: api/v1/history/

    """

    lookup_field = 'video_id'
    permission_classes = [IsAuthenticated]
    pagination_class = HistoryCursorPagination
    serializer_class = video_serializers.VideoHistorySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoHistoryService = container.resolve(BaseVideoHistoryService)
        self.logger: Logger = container.resolve(Logger)

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
            ),
        ],
    )
    @action(methods=['post'], detail=False, url_path='add', url_name='add')
    def add_video_in_history(self, request):
        """API endpoint to add video in watching history.

        To add video you need to provide required query parameter - 'v' with video_id.
        Example: api/v1/history/add/?v=au90D2BoHuT

        """
        video_id = request.query_params.get('v')

        try:
            result = self.service.add_video_in_history(user=request.user, video_id=video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to delete from history.',
                required=True,
                type=str,
            ),
        ],
    )
    @action(methods=['delete'], url_path='delete', url_name='delete', detail=False)
    def delete_video_from_history(self, request):
        """API endpoint to delete video from watching history.

        To delete video you need to provide required query parameter - 'v' with video_id.

        Example: api/v1/history/delete/?v=au90D2BoHuT

        """
        video_id = request.query_params.get('v')

        try:
            result = self.service.delete_video_from_history(user=request.user, video_id=video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_204_NO_CONTENT)


class MyVideoView(generics.ListAPIView):
    """API endpoint to get all user's videos.

    Supports cursor pagination.

    Example: api/v1/videos-personal/

    """

    serializer_class = video_serializers.VideoPreviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        return Video.objects.all().filter(author=self.request.user.channel).select_related('author')


class PlaylistAPIView(viewsets.ModelViewSet):
    """API endpoint to list/retrieve/create/update/delete playlists.

    Permissions and access:
    - create: authenticated only
    - list: authenticated only
    - retrieve: allow any if not private
    - delete and update: author or staff only

    Example: api/v1/playlist/, api/v1/playlist/kn2puLWEDmqIvavBgvYRSypsb162jSHE/

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
            return video_serializers.PlaylistPreviewSerializer
        return video_serializers.PlaylistSerializer

    def get_queryset(self):
        if self.action == 'list':
            return self.service.get_playlists_for_listing(self.request.user)
        if self.action == 'retrieve':
            return self.service.get_playlists_for_retrieving()
        return self.service.playlist_repository.get_all_playlists()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video to add to playlist.',
                required=True,
                type=str,
            ),
        ],
    )
    @action(
        methods=['post'],
        url_name='add-video',
        url_path='add-video',
        detail=True,
    )
    def add_video_in_playlist(self, request, id):
        """API endpoint to add video in playlist.

        Requires 'playlist id' in URL and 'v' query param which contains video_id.

        Example: /api/v1/playlist/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/add-video/?v=33CjPuGJsEZ

        """
        video_id = request.query_params.get('v')

        try:
            result = self.service.add_video_in_playlist(playlist_id=id, video_id=video_id)
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

        Example: /api/v1/playlist/W9MghI-EVXdkfYzfuvUmCCWlJRcPm1FT/delete-video/?v=33CjPuGJsEZ

        """
        video_id = request.query_params.get('v')

        try:
            result = self.service.delete_video_from_playlist(playlist_id=id, video_id=video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_204_NO_CONTENT)
