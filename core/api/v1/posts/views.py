from logging import Logger

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import orjson
import punq
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from core.api.v1.posts.serializers.post_serializers import (
    PostDetailedSerializer,
    PostInSerializer,
    PostLikeCreateInSerializer,
    PostLikeCreateOutSerializer,
    PostLikeDeleteOutSerializer,
    PostOutSerializer,
    PostSerializer,
)
from core.apps.common.exceptions import ServiceException
from core.apps.common.mixins import CustomViewMixin
from core.apps.common.pagination import CustomCursorPagination
from core.apps.common.permissions import IsAuthenticatedOrAuthorOrAdminOrReadOnly
from core.apps.common.services.cache import BaseCacheService
from core.apps.posts.services.posts import BasePostService
from core.apps.posts.use_cases.create_post import PostCreateUseCase
from core.apps.posts.use_cases.create_post_like import PostLikeCreateUseCase
from core.apps.posts.use_cases.delete_post_like import PostLikeDeleteUseCase
from core.apps.posts.use_cases.get_channel_posts import GetChannelPostsUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


# TODO: tests, comments and likes for them
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

    @extend_schema(request=PostInSerializer, responses=PostOutSerializer)
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

        return Response(PostOutSerializer(result).data, status=201)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='s',
                description="Parameter identifying channel's slug to get related 'Posts'",
                required=True,
                type=str,
            ),
        ],
        summary="Get channel's posts",
    )
    def list(self, request, *args, **kwargs):
        use_case: GetChannelPostsUseCase = self.container.resolve(GetChannelPostsUseCase)
        slug = request.query_params.get('s')
        cache_key = f"{settings.CACHE_KEYS.get('related_posts')}{slug}_{request.query_params.get('c', '1')}"

        cached_data = self.cache_service.get_cached_data(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            qs = use_case.execute(
                slug=slug,
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return self.mixin_cache_and_response(
            cache_key=cache_key,
            timeout=60 * 2,
            queryset=qs,
        )

    @extend_schema(
        request=PostLikeCreateInSerializer,
        responses=PostLikeCreateOutSerializer,
        summary='Like or dislike post',
    )
    @action(methods=['post'], detail=True, url_path='like')
    def like_create(self, request, post_id):
        use_case: PostLikeCreateUseCase = self.container.resolve(PostLikeCreateUseCase)

        serializer = PostLikeCreateInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = use_case.execute(
                user=user_to_entity(request.user),
                post_id=post_id,
                is_like=serializer.validated_data.get('is_like'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        responses=PostLikeDeleteOutSerializer,
        summary="Delete Post's like or dislike",
    )
    @action(url_path='unlike', methods=['delete'], detail=True)
    def like_delete(self, request, post_id):
        use_case: PostLikeDeleteUseCase = self.container.resolve(PostLikeDeleteUseCase)

        try:
            result = use_case.execute(user=user_to_entity(request.user), post_id=post_id)

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(result, status.HTTP_204_NO_CONTENT)
