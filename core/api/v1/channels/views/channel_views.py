from logging import Logger

import orjson
import punq
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import (
    generics,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from core.api.v1.channels.serializers import (
    ChannelAboutSerializer,
    ChannelAndVideosSerializer,
    ChannelSerializer,
    SubscriptionInSerializer,
    SubscriptionSerializer,
)
from core.api.v1.common.serializers.serializers import DetailOutSerializer
from core.api.v1.schema.response_examples.common import (
    build_example_response_from_error,
    created_response_example,
    deleted_response_example,
)
from core.apps.channels.converters.channels import channel_from_entity
from core.apps.channels.exceptions.channels import ChannelWithSlugNotFoundError
from core.apps.channels.exceptions.subscriptions import (
    SelfSubscriptionError,
    SubscriptionDoesNotExistError,
    SubscriptionExistsError,
)
from core.apps.channels.models import (
    Channel,
    SubscriptionItem,
)
from core.apps.channels.services.channels import (
    BaseChannelAboutService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
)
from core.apps.channels.use_cases.channels.delete_channel import DeleteChannelUseCase
from core.apps.common.constants import CACHE_KEYS
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.common.mixins import CustomViewMixin
from core.apps.common.pagination import CustomCursorPagination
from core.apps.common.services.cache import BaseCacheService
from core.apps.payments.exceptions import StripeSubStillActiveError
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@extend_schema_view(
    get=extend_schema(summary='Retrieve channel'),
    put=extend_schema(summary='Update channel PUT'),
    patch=extend_schema(summary='Update channel PATCH'),
    delete=extend_schema(
        responses={
            204: None,
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='The user cannot delete the channel due to an active subscription',
            ),
        },
        examples=[
            build_example_response_from_error(error=StripeSubStillActiveError),
        ],
        summary='Delete channel',
    ),
)
class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container: punq.Container = get_container()
        self.logger: Logger = self.container.resolve(Logger)
        self.channel_service: BaseChannelService = self.container.resolve(BaseChannelService)
        self.cache_service: BaseCacheService = self.container.resolve(BaseCacheService)
        self.logger: Logger = self.container.resolve(Logger)

    def get_object(self):
        channel = self.channel_service.repository.get_channel_by_user_or_none(
            user=user_to_entity(self.request.user),
        )
        return channel_from_entity(channel) if channel else None

    def delete(self, request, *args, **kwargs):
        use_case: DeleteChannelUseCase = self.container.resolve(DeleteChannelUseCase)

        try:
            use_case.execute(user=user_to_entity(request.user))

        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        user = user_to_entity(request.user)
        cache_key = f'{CACHE_KEYS.get("retrieve_channel")}{user.id}'

        cached_data = self.cache_service.get(cache_key)

        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)

        try:
            channel = self.channel_service.get_channel_by_user_or_404(user)
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        serializer = self.get_serializer(channel)
        self.cache_service.set(cache_key, serializer.data, 60 * 15)

        return Response(serializer.data, status.HTTP_200_OK)


@extend_schema(summary='Get list of subscribers')
class ChannelSubscribersView(generics.ListAPIView, CustomViewMixin):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomCursorPagination
    queryset = SubscriptionItem.objects.all()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.sub_service: BaseChannelSubsService = container.resolve(BaseChannelSubsService)
        self.channel_service: BaseChannelService = container.resolve(BaseChannelService)
        self.cache_service: BaseCacheService = container.resolve(BaseCacheService)

    def list(self, request, *args, **kwargs):
        channel = self.channel_service.get_channel_by_user_or_404(user_to_entity(request.user))

        cache_key = f'{CACHE_KEYS.get("subs_list")}{channel.id}_{request.query_params.get("c", "1")}'
        cached_data = self.cache_service.get(cache_key)

        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)

        return self.mixin_cache_and_response(
            queryset=self.sub_service.get_subscriber_list(channel=channel),
            cache_key=cache_key,
            timeout=60 * 15,
        )


@extend_schema(summary='Get channel main page: channel info and last 5 public videos')
class ChannelMainView(generics.RetrieveAPIView):
    """Main page includes info about channel and last 5 public videos."""

    serializer_class = ChannelAndVideosSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'
    throttle_scope = 'channel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseChannelMainService = container.resolve(BaseChannelMainService)

    def get_queryset(self):
        return self.service.get_channel_main_page_list()


@extend_schema(summary='Get detailed info about channel')
class ChannelAboutView(generics.RetrieveAPIView):
    serializer_class = ChannelAboutSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseChannelAboutService = container.resolve(BaseChannelAboutService)

    def get_queryset(self):
        return self.service.get_channel_about_list()

    @method_decorator(cache_page(60 * 15, key_prefix='channel_about'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema_view(
    subscribe=extend_schema(
        responses={
            201: OpenApiResponse(response=DetailOutSerializer, description='Subscription has been created'),
            400: OpenApiResponse(
                response=DetailOutSerializer,
                description='Self subscription or subscription already exsists',
            ),
            404: OpenApiResponse(response=DetailOutSerializer, description='Channel was not found'),
        },
        examples=[
            created_response_example(),
            build_example_response_from_error(error=ChannelWithSlugNotFoundError),
            build_example_response_from_error(error=SelfSubscriptionError),
            build_example_response_from_error(error=SubscriptionExistsError),
        ],
        summary='Create channel subscription',
    ),
    unsubscribe=extend_schema(
        responses={
            200: OpenApiResponse(response=DetailOutSerializer, description='Subscription has been deleted'),
            400: OpenApiResponse(response=DetailOutSerializer, description='Self subscription'),
            404: OpenApiResponse(
                response=DetailOutSerializer,
                description='Channel slug was not found or subscription does not exists',
            ),
        },
        examples=[
            deleted_response_example(),
            build_example_response_from_error(error=SelfSubscriptionError),
            build_example_response_from_error(error=ChannelWithSlugNotFoundError),
            build_example_response_from_error(error=SubscriptionDoesNotExistError),
        ],
        summary='Delete channel subscription',
    ),
)
class SubscriptionAPIView(viewsets.GenericViewSet):
    queryset = SubscriptionItem.objects.all()
    serializer_class = SubscriptionInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container: punq.Container = get_container()
        self.service: BaseSubscriptionService = container.resolve(BaseSubscriptionService)
        self.logger: Logger = container.resolve(Logger)

    @action(methods=['post'], url_path='subscribe', detail=False)
    def subscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.subscribe(
                user=user_to_entity(request.user),
                channel_slug=serializer.validated_data.get('channel_slug'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        else:
            return Response(result, status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='unsubscribe', detail=False)
    def unsubscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = self.service.unsubscribe(
                user=user_to_entity(request.user),
                channel_slug=serializer.validated_data.get('channel_slug'),
            )
        except ServiceException as error:
            self.logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise
        else:
            return Response(result, status.HTTP_200_OK)
