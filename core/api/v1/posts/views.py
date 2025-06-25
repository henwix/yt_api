from logging import Logger

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import orjson
import punq
from drf_spectacular.utils import extend_schema

from core.api.v1.posts.serializers import (
    PostDetailedSerializer,
    PostInSerializer,
    PostOutSerializer,
    PostSerializer,
)
from core.apps.common.exceptions import ServiceException
from core.apps.common.pagination import CustomCursorPagination
from core.apps.common.permissions import IsAuthenticatedOrAuthorOrAdminOrReadOnly
from core.apps.posts.services.posts import BasePostService
from core.apps.posts.use_cases.create_post import CreatePostUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


#  TODO: get, update, delete with new Serializers and 'queryset' or 'get_queryset' + get_channels_posts endpoint
class PostAPIViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    lookup_field = 'post_id'
    lookup_url_kwarg = 'post_id'
    permission_classes = [IsAuthenticatedOrAuthorOrAdminOrReadOnly]
    pagination_class = CustomCursorPagination

    def __init__(self, **kwargs):
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)
        self.service: BasePostService = self.container.resolve(BasePostService)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostDetailedSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return PostSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return self.service.get_posts_for_retrieving()
        return self.service.get_all_posts()

    @extend_schema(request=PostInSerializer, responses=PostOutSerializer)
    def create(self, request):
        use_case: CreatePostUseCase = self.container.resolve(CreatePostUseCase)

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
