from logging import Logger

from django.conf import settings
from rest_framework import (
    filters,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from core.api.v1.common.serializers.comments import (
    PkLikeSerializer,
    PkParameterSerializer,
    PostLikeSerializer,
)
from core.api.v1.common.serializers.serializers import (
    DetailOutSerializer,
    LikeCreateInSerializer,
    LikeCreateOutSerializer,
    SParameterSerializer,
)
from core.api.v1.posts.serializers.post_comment_serializers import (
    CommentCreateSerializer,
    CommentRetrieveSerializer,
    CommentUpdateSerializer,
)
from core.api.v1.posts.serializers.post_serializers import (
    PostDetailedSerializer,
    PostInSerializer,
    PostOutSerializer,
    PostSerializer,
    PostUIDSerializer,
)
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    build_paginated_response_based_on_serializer,
    deleted_response_example,
    like_created_response_example,
)
from core.api.v1.videos.serializers.video_serializers import CommentCreatedSerializer
from core.apps.channels.exceptions.channels import ChannelNotFoundError
from core.apps.common.exceptions.comments import (
    CommentLikeNotFoundError,
    CommentNotFoundError,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.mixins import CustomViewMixin
from core.apps.common.pagination import CustomCursorPagination
from core.apps.common.permissions.permissions import (
    IsAuthenticatedOrAuthorOrAdminOrReadOnly,
    IsAuthenticatedOrAuthorOrReadOnly,
)
from core.apps.common.services.cache import BaseCacheService
from core.apps.posts.converters.posts import post_to_entity
from core.apps.posts.exceptions import (
    PostLikeNotFoundError,
    PostNotFoundError,
)
from core.apps.posts.services.comments import BasePostCommentService
from core.apps.posts.services.posts import BasePostService
from core.apps.posts.use_cases.posts.create_post import PostCreateUseCase
from core.apps.posts.use_cases.posts.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.posts.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.posts.get_channel_posts import GetChannelPostsUseCase
from core.apps.posts.use_cases.posts_comments.create_comment import CreatePostCommentUseCase
from core.apps.posts.use_cases.posts_comments.get_list_comments import GetPostCommentsUseCase
from core.apps.posts.use_cases.posts_comments.get_replies_list_comments import GetPostCommentRepliesUseCase
from core.apps.posts.use_cases.posts_comments.like_create import PostCommentLikeCreateUseCase
from core.apps.posts.use_cases.posts_comments.like_delete import PostCommentLikeDeleteUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@extend_schema_view(
    create=extend_schema(
        request=PostInSerializer,
        responses={
            201: OpenApiResponse(
                response=PostOutSerializer,
                description='Post has been created',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel is not found',
            ),
        },
        examples=[
            build_example_response_from_error(error=ChannelNotFoundError),
        ],
        summary='Create a new post',
    ),
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='s',
                description="Parameter identifying channel's slug",
                required=True,
                type=str,
                examples=[
                    OpenApiExample(
                        name='ChannelSlugExample',
                        value='henwix',
                        summary="Channel's slug",
                    ),
                ],
            ),
        ],
        summary="Get channel's posts",
    ),
    like_create=extend_schema(
        request=LikeCreateInSerializer,
        responses={
            201: OpenApiResponse(
                response=LikeCreateOutSerializer,
                description='Reaction(like or dislike) has been created',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Post or Channel was not found',
            ),
        },
        examples=[
            like_created_response_example(),
            build_example_response_from_error(error=PostNotFoundError),
            build_example_response_from_error(error=ChannelNotFoundError),
        ],
        summary='Create reaction to a post',
    ),
    like_delete=extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Reaction(like or dislike) has been deleted',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel, Post or PostLike was not found',
            ),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=ChannelNotFoundError),
            build_example_response_from_error(error=PostNotFoundError),
            build_example_response_from_error(error=PostLikeNotFoundError),
        ],
        summary='Delete reaction to a post',
    ),
    retrieve=extend_schema(summary='Retrieve post'),
    update=extend_schema(summary='Update post PUT'),
    partial_update=extend_schema(summary='Update post PATCH'),
    destroy=extend_schema(summary='Delete post'),
)
class PostAPIViewset(ModelViewSet, CustomViewMixin):
    lookup_field = 'post_id'
    lookup_url_kwarg = 'post_id'
    permission_classes = [IsAuthenticatedOrAuthorOrAdminOrReadOnly]
    pagination_class = CustomCursorPagination

    def __init__(self, **kwargs):
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)
        self.post_service: BasePostService = self.container.resolve(BasePostService)
        self.cache_service: BaseCacheService = self.container.resolve(BaseCacheService)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostDetailedSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return PostSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return self.post_service.get_posts_for_retrieving()
        return self.post_service.get_all_posts()

    def create(self, request):
        use_case: PostCreateUseCase = self.container.resolve(PostCreateUseCase)

        serializer = PostInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                text=serializer.validated_data.get('text'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(PostOutSerializer(result).data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        use_case: GetChannelPostsUseCase = self.container.resolve(GetChannelPostsUseCase)

        serializer = SParameterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        slug = serializer.validated_data.get('s')
        cache_key = f"{settings.CACHE_KEYS.get('related_posts')}{slug}_{request.query_params.get('c', '1')}"

        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            qs = use_case.execute(slug=slug)

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return self.mixin_cache_and_response(
            cache_key=cache_key,
            timeout=60 * 2,
            queryset=qs,
        )

    @action(methods=['post'], detail=True, url_path='like')
    def like_create(self, request, post_id):
        use_case: PostLikeCreateUseCase = self.container.resolve(PostLikeCreateUseCase)

        serializer = PostLikeSerializer(data={'is_like': request.data.get('is_like', True), 'post_id': post_id})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                post_id=serializer.validated_data.get('post_id'),
                is_like=serializer.validated_data.get('is_like'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, post_id):
        use_case: PostLikeDeleteUseCase = self.container.resolve(PostLikeDeleteUseCase)

        serializer = PostLikeSerializer(data={'post_id': post_id})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                post_id=serializer.validated_data.get('post_id'),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_200_OK)


@extend_schema_view(
    create=extend_schema(
        responses={
            201: OpenApiResponse(
                response=CommentCreatedSerializer,
                description='Comment has been created',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel was not found',
            ),
        },
        examples=[
            build_example_response_from_error(error=ChannelNotFoundError),
        ],
        summary='Create a new post comment',
    ),
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='p',
                description="Parameter identifying post id",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=CommentRetrieveSerializer,
                description='List of comments to the post has been retrived',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Post was not found',
            ),
        },
        examples=[
            build_example_response_from_error(error=PostNotFoundError),
        ],
        summary="Get post's comments",
    ),
    get_replies_list=extend_schema(
        responses=build_paginated_response_based_on_serializer(
            serializer=CommentRetrieveSerializer,
            pagination_type='cursor',
            description='Replies have been retrived',
        ),
        summary="Get post comment's replies",
    ),
    like_create=extend_schema(
        request=LikeCreateInSerializer,
        responses={
            201: OpenApiResponse(
                response=LikeCreateOutSerializer,
                description='Reaction has been created',
            ),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel or comment was not found',
            ),
        },
        examples=[
            like_created_response_example(),
            build_example_response_from_error(error=ChannelNotFoundError),
            build_example_response_from_error(error=CommentNotFoundError),
        ],
        summary='Create reaction to a post comment',
    ),
    like_delete=extend_schema(
        responses={
            200: OpenApiResponse(
                response=DetailOutSerializer,
                description='Reaction has been deleted',
            ),
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
        summary='Delete reaction to a post comment',
    ),
    retrieve=extend_schema(summary='Retrieve post comment'),
    update=extend_schema(summary='Update post comment PUT'),
    partial_update=extend_schema(summary='Update post comment PATCH'),
    destroy=extend_schema(summary='Delete post comment'),
)
class CommentPostAPIView(
    ModelViewSet,
    CustomViewMixin,
):
    pagination_class = CustomCursorPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-likes_count']
    permission_classes = [IsAuthenticatedOrAuthorOrReadOnly]

    def __init__(self, **kwargs):
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)
        self.post_service: BasePostCommentService = self.container.resolve(BasePostCommentService)
        self.cache_service: BaseCacheService = self.container.resolve(BaseCacheService)

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentRetrieveSerializer

    def get_queryset(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return self.post_service.get_all_comments()
        return self.post_service.get_comments_for_retrieving()

    def filter_queryset(self, queryset):
        if self.action in ['list']:
            return super().filter_queryset(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        use_case: CreatePostCommentUseCase = self.container.resolve(CreatePostCommentUseCase)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                post=post_to_entity(serializer.validated_data.get('post')),
                text=serializer.validated_data.get('text'),
                reply_comment_id=getattr(serializer.validated_data.get('reply_comment'), 'pk', None),
            )

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        return Response(CommentCreatedSerializer(result).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.post_service.change_updated_status(comment_id=kwargs.get('pk'), is_updated=True)
        return response

    def list(self, request, *args, **kwargs):
        use_case: GetPostCommentsUseCase = self.container.resolve(GetPostCommentsUseCase)

        serializer = PostUIDSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            qs = use_case.execute(
                post_id=serializer.validated_data.get('p'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filtration_and_pagination(qs)
        return result

    @action(url_path='replies', url_name='replies', detail=True)
    def get_replies_list(self, request, pk):
        use_case: GetPostCommentRepliesUseCase = self.container.resolve(GetPostCommentRepliesUseCase)

        serializer = PkParameterSerializer(data={'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            qs = use_case.execute(comment_id=serializer.validated_data.get('pk'))
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        result = self.mixin_filtration_and_pagination(qs)
        return result

    @action(methods=['post'], url_path='like', detail=True)
    def like_create(self, request, pk):
        use_case: PostCommentLikeCreateUseCase = self.container.resolve(PostCommentLikeCreateUseCase)

        serializer = PkLikeSerializer(data={'is_like': request.data.get('is_like', True), 'pk': pk})
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                comment_id=pk,
                is_like=serializer.validated_data.get('is_like'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @action(methods=['delete'], url_path='unlike', detail=True)
    def like_delete(self, request, pk):
        use_case: PostCommentLikeDeleteUseCase = self.container.resolve(PostCommentLikeDeleteUseCase)

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
