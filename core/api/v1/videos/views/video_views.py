from logging import Logger

from rest_framework import (
    filters,
    generics,
    mixins,
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
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)

from core.api.v1.common.serializers.comments import (
    PkLikeSerializer,
    PkParameterSerializer,
    VideoIdParameterSerializer,
    VideoLikeSerializer,
)
from core.api.v1.common.serializers.playlists import PlaylistIdParameterSerializer
from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    LikeCreateInSerializer,
    LikeCreateOutSerializer,
    VParameterSerializer,
)
from core.api.v1.schema.enums.common import build_enum_query_param
from core.api.v1.schema.enums.videos import VideoSearchOrderingEnum
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    build_paginated_response_based_on_serializer,
    created_response_example,
    deleted_response_example,
    detail_response_example,
    like_created_response_example,
)
from core.api.v1.schema.response_examples.videos import video_id_openapi_parameter
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
from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.common.exceptions.comments import (
    CommentLikeNotFoundError,
    CommentNotFoundError,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.mixins import CustomViewMixin
from core.apps.common.pagination import (
    CustomCursorPagination,
    CustomPageNumberPagination,
)
from core.apps.common.permissions.permissions import IsAuthenticatedOrAuthorOrReadOnly
from core.apps.users.converters.users import user_to_entity
from core.apps.videos.converters.videos import video_to_entity
from core.apps.videos.exceptions.playlists import (
    PlaylistIdNotProvidedError,
    PlaylistNotFoundError,
    PlaylistPermissionError,
    VideoDoesNotExistInPlaylistError,
)
from core.apps.videos.exceptions.videos import (
    PrivateVideoOrUploadingError,
    PrivateVideoPermissionError,
    VideoDoesNotExistInHistoryError,
    VideoIdNotProvidedError,
    VideoLikeNotFoundError,
    VideoNotFoundByVideoIdError,
    ViewExistsError,
)
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
from core.apps.videos.use_cases.playlists.playlist_videos import GetPlaylistVideosUseCase
from core.project.containers import get_container


@extend_schema_view(
    like_create=extend_schema(
        request=LikeCreateInSerializer,
        responses={
            201: OpenApiResponse(response=LikeCreateOutSerializer, description='Reaction has been created'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video was not found'),
        },
        examples=[
            like_created_response_example(),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
        ],
        summary='Create reaction to a video',
    ),
    like_delete=extend_schema(
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Reaction has been deleted'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video or video reaction was not found'),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=VideoLikeNotFoundError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
        ],
        summary='Delete reaction to a video',
    ),
    view_create=extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(response=DetailOutSerializer, description='View has been created'),
            400: OpenApiResponse(response=DetailOutSerializer, description='View already exists'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video was not found'),
        },
        examples=[
            created_response_example(),
            build_example_response_from_error(error=ViewExistsError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
        ],
        summary='Create view to a video',
        description='Allows add a view if the previous one was created more than 24 hours ago',
    ),
    list=extend_schema(
        parameters=[
            build_enum_query_param(
                name='ordering',
                enum=VideoSearchOrderingEnum,
                description='Which field to use when ordering the results',
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=VideoPreviewSerializer,
                description='List of videos after searching has been retrieved',
            ),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='No results found',
            ),
        },
        examples=[
            detail_response_example(
                name='No results found',
                value='No results found. Try different keywords or remove search filters',
                status_code=400,
            ),
        ],
        summary='Search video',
    ),
    destroy=extend_schema(summary='Delete video'),
    retrieve=extend_schema(summary='Retrieve video'),
    update=extend_schema(summary='Update video PUT'),
    partial_update=extend_schema(summary='Update video PATCH'),
)
class VideoViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
):
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
    ordering_fields = ['created_at']
    throttle_scope = 'video'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseVideoService = container.resolve(BaseVideoService)
        self.logger: Logger = container.resolve(Logger)

    @action(url_path='like', methods=['post'], detail=True)
    def like_create(self, request, video_id):
        serializer = VideoLikeSerializer(data={'is_like': request.data.get('is_like', True), 'video_id': video_id})
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.like_create(
                user=user_to_entity(request.user),
                video_id=video_id,
                is_like=serializer.validated_data.get('is_like', True),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, video_id):
        serializer = VideoIdParameterSerializer(data={'video_id': video_id})
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.like_delete(user=user_to_entity(request.user), video_id=video_id)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)

    @action(url_path='view', methods=['post'], detail=True)
    def view_create(self, request, video_id):
        """API endpoint for adding views to videos.

        Have no required fields.

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
            return Response(
                data={'detail': 'No results found. Try different keywords or remove search filters'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        video_pre_delete.send(sender=Video, instance=instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    @extend_schema(
        responses={
            201: OpenApiResponse(response=CommentCreatedSerializer, description='Video comment has been created'),
            403: OpenApiResponse(response=DetailOutSerializer, description='Video access denied'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Channel was not found'),
        },
        examples=[
            build_example_response_from_error(error=PrivateVideoOrUploadingError),
            build_example_response_from_error(error=ChannelNotFoundError),
        ],
        summary='Create a new video comment',
    )
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
                description="Parameter identifying video id",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=VideoCommentSerializer,
                description='List of comments to the video has been retrived',
            ),
            403: OpenApiResponse(response=DetailOutSerializer, description='Video access denied'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video was not found'),
        },
        examples=[
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
            build_example_response_from_error(error=PrivateVideoPermissionError),
        ],
        summary="Get video's comments",
    )
    def list(self, request, *args, **kwargs):
        use_case: GetVideoCommentsUseCase = self.container.resolve(GetVideoCommentsUseCase)

        serializer = VParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            qs = use_case.execute(
                user=user_to_entity(request.user),
                video_id=serializer.validated_data.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filtration_and_pagination(qs)
        return result

    @extend_schema(summary='Update video comment PUT')
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.service.change_updated_status(comment_id=kwargs.get('pk'), is_updated=True)
        return response

    @extend_schema(summary='Update video comment PATCH')
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='Retrieve video comment')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary='Delete video comment')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: build_paginated_response_based_on_serializer(
                serializer=VideoCommentSerializer,
                pagination_type='cursor',
                description='Replies have been retrieved',
            ),
            404: OpenApiResponse(response=DetailOutSerializer, description='Comment was not found'),
        },
        examples=[
            build_example_response_from_error(error=CommentNotFoundError),
        ],
        summary="Get comment's replies",
    )
    @action(url_path='replies', url_name='replies', detail=True)
    def get_replies_list(self, request, pk):
        serializer = PkParameterSerializer(data={'pk': pk})
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
        responses={
            201: OpenApiResponse(response=LikeCreateOutSerializer, description='Reaction has been created'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Channel or comment was not found'),
        },
        examples=[
            like_created_response_example(),
            build_example_response_from_error(error=ChannelNotFoundError),
            build_example_response_from_error(error=CommentNotFoundError),
        ],
        summary='Create reaction to a video comment',
    )
    @action(methods=['post'], url_path='like', detail=True)
    def like_create(self, request, pk):
        use_case: VideoCommentLikeCreateUseCase = self.container.resolve(VideoCommentLikeCreateUseCase)
        is_like = request.data.get('is_like', True)

        serializer = PkLikeSerializer(data={'is_like': is_like, 'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                comment_id=serializer.validated_data.get('pk'),
                is_like=serializer.validated_data.get('is_like'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Reaction has been deleted'),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel, comment or comment reaction was not found',
            ),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=ChannelNotFoundError),
            build_example_response_from_error(error=CommentNotFoundError),
            build_example_response_from_error(error=CommentLikeNotFoundError),
        ],
        summary='Delete reaction to a video comment',
    )
    @action(methods=['delete'], url_path='unlike', detail=True)
    def like_delete(self, request, pk):
        use_case: VideoCommentLikeDeleteUseCase = self.container.resolve(VideoCommentLikeDeleteUseCase)

        serializer = PkParameterSerializer(data={'pk': pk})
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

    @extend_schema(summary='Get list of videos in history')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Video history has been cleared'),
            400: OpenApiResponse(response=DetailOutSerializer, description='History is empty'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Channel was not found'),
        },
        examples=[
            deleted_response_example(),
            detail_response_example(
                name='History is empty',
                value='History is empty',
                status_code=400,
            ),
            build_example_response_from_error(error=ChannelNotFoundError),
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
            video_id_openapi_parameter(),
        ],
        responses={
            201: OpenApiResponse(
                response=DetailOutSerializer,
                description='Video has been added to the history or already exists in history',
            ),
            400: OpenApiResponse(response=DetailOutSerializer, description='Video id was not provided'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video was not found'),
        },
        examples=[
            detail_response_example(
                name='Video added in history',
                value='Success',
                status_code=201,
            ),
            detail_response_example(
                name='Video already exists in history',
                value='Video already exists in history, watched_at has been updated',
                status_code=201,
            ),
            build_example_response_from_error(error=VideoIdNotProvidedError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
        ],
        summary='Add video to history',
    )
    @action(methods=['post'], detail=False, url_path='add', url_name='add')
    def add_video_in_history(self, request):
        serializer = VParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.add_video_in_history(
                user=user_to_entity(request.user),
                video_id=serializer.validated_data.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        request=None,
        parameters=[
            video_id_openapi_parameter(),
        ],
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Video has been deleted from the history'),
            400: OpenApiResponse(response=DetailOutSerializer, description='Video id was not provided'),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Video was not found or not found in the history',
            ),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=VideoIdNotProvidedError),
            build_example_response_from_error(error=VideoDoesNotExistInHistoryError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
        ],
        summary='Delete video from history',
    )
    @action(methods=['delete'], url_path='delete', url_name='delete', detail=False)
    def delete_video_from_history(self, request):
        serializer = VParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.delete_video_from_history(
                user=user_to_entity(request.user),
                video_id=serializer.validated_data.get('v'),
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


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=VideoPreviewSerializer(many=True),
            description='Videos in playlist have been retrieved',
        ),
        403: OpenApiResponse(response=DetailOutSerializer, description='Playlist permission denied'),
        404: OpenApiResponse(response=DetailOutSerializer, description='Playlist was not found'),
    },
    examples=[
        build_example_response_from_error(error=PlaylistNotFoundError),
        build_example_response_from_error(error=PlaylistPermissionError),
    ],
    summary="Get playlist's videos",
)
class PlaylistVideosView(generics.ListAPIView, CustomViewMixin):
    serializer_class = VideoPreviewSerializer
    pagination_class = CustomCursorPagination

    def list(self, request, id):
        container: punq.Container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: GetPlaylistVideosUseCase = container.resolve(GetPlaylistVideosUseCase)

        serializer = PlaylistIdParameterSerializer(data={'id': id})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(playlist_id=id, user=user_to_entity(request.user))
        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return self.mixin_filtration_and_pagination(result)


class PlaylistAPIView(viewsets.ModelViewSet):
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

    @extend_schema(summary='Create playlist')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary='Delete playlist')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(summary='Update platlist PUT')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary='Update playlist PATCH')
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='Retrieve playlist')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary='Get all personal channel playlists')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=None,
        parameters=[
            video_id_openapi_parameter(),
        ],
        responses={
            201: OpenApiResponse(response=DetailOutSerializer, description='Video has been added in playlist'),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Video already exists in playlist, video id or playlist id was not provided',
            ),
            403: OpenApiResponse(response=DetailOutSerializer, description='Playlist permission denied'),
            404: OpenApiResponse(response=DetailOutSerializer, description='Video or playlist was not found'),
        },
        examples=[
            detail_response_example(
                name='Added',
                value='Success',
                status_code=201,
            ),
            detail_response_example(
                name='Video already exists in that playlist',
                value='Video already exists in that playlist',
                status_code=400,
            ),
            build_example_response_from_error(error=VideoIdNotProvidedError),
            build_example_response_from_error(error=PlaylistIdNotProvidedError),
            build_example_response_from_error(error=PlaylistPermissionError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
            build_example_response_from_error(error=PlaylistNotFoundError),
        ],
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
        serializer = VParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            added, result = self.service.add_video_in_playlist(
                user=user_to_entity(request.user),
                playlist_id=id,
                video_id=serializer.validated_data.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED if added else status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='v',
                description='Parameter identifying video id',
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Video has been deleted from playlist'),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Video id or playlist id was not provided',
            ),
            403: OpenApiResponse(response=DetailOutSerializer, description='Playlist permission error'),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Video not exists in playlist, video or playlist was not found',
            ),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=VideoIdNotProvidedError),
            build_example_response_from_error(error=PlaylistIdNotProvidedError),
            build_example_response_from_error(error=PlaylistPermissionError),
            build_example_response_from_error(error=VideoDoesNotExistInPlaylistError),
            build_example_response_from_error(error=VideoNotFoundByVideoIdError),
            build_example_response_from_error(error=PlaylistNotFoundError),
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
        serializer = VParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.delete_video_from_playlist(
                user=user_to_entity(request.user),
                playlist_id=id,
                video_id=serializer.validated_data.get('v'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)
