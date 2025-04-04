import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import (
    generics,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiTypes,
)

from core.apps.common.mixins import PaginationMixin
from core.apps.common.pagination import CustomCursorPagination
from core.apps.common.services.cache import BaseCacheService
from core.project.containers import get_container

from . import serializers
from .models import (
    Channel,
    SubscriptionItem,
)
from .services.channels import (
    BaseChannelAboutService,
    BaseChannelAvatarService,
    BaseChannelMainService,
    BaseChannelService,
    BaseChannelSubsService,
    BaseSubscriptionService,
)


log = logging.getLogger(__name__)


# TODO: Add endpoint to create/delete channels
class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for detail, update and delete 'Channel' instances.

    If the request method is DELETE, related/associated 'User' will also be deleted.

    Example: /api/v1/channel/

    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.channel_service: BaseChannelService = container.resolve(BaseChannelService)
        self.cache_service: BaseCacheService = container.resolve(BaseCacheService)

    def get_object(self):
        return self.channel_service.repository.get_channel_by_user(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        cache_key = f'retrieve_channel_{user.pk}'

        cached_data = self.cache_service.get_cached_data(cache_key)

        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)

        channel = self.channel_service.get_channel(user)
        serializer = self.get_serializer(channel)
        self.cache_service.cache_data(cache_key, serializer.data, 60 * 15)

        return Response(serializer.data, status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.channel_service.delete_channel(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChannelSubscribersView(generics.ListAPIView, PaginationMixin):
    """API endpoint to channel's subscribers listing.

    Supports cache for 15 minutes and Cursor pagination.
    Example: /api/v1/channel/subscribers/

    """

    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomCursorPagination
    queryset = SubscriptionItem.objects.all()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.sub_service: BaseChannelSubsService = container.resolve(BaseChannelSubsService)
        self.cache_service: BaseCacheService = container.resolve(BaseCacheService)

    def list(self, request, *args, **kwargs):
        """Custom list method to cache response."""

        cache_key = f'subs_{request.user.pk}_{request.query_params.get("c", "1")}'

        cached_data = self.cache_service.get_cached_data(cache_key)

        if cached_data:
            return Response(cached_data, status.HTTP_200_OK)

        qs = self.filter_queryset(self.sub_service.get_subscriber_list(channel=request.user.channel))
        paginated_response = self.mixin_pagination(qs)

        if paginated_response:
            self.cache_service.cache_data(cache_key, paginated_response.data, 60 * 15)
            return paginated_response

        serializer = self.get_serializer(qs, many=True)
        self.cache_service.cache_data(cache_key, serializer.data, 60 * 15)

        response = Response(serializer.data, status.HTTP_200_OK)
        return response


class ChannelAvatarDestroy(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseChannelAvatarService = container.resolve(BaseChannelAvatarService)

    def delete(self, request):
        result = self.service.delete_avatar(request.user)
        return Response(result, status.HTTP_204_NO_CONTENT)


class ChannelMainView(generics.RetrieveAPIView):
    """API endpoint to get channel main page. Main page includes info about
    channel and last 5 public videos.

    Example: /api/v1/c/henwixchannel

    """

    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'
    throttle_scope = 'channel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseChannelMainService = container.resolve(BaseChannelMainService)

    def get_queryset(self):
        return self.service.get_channel_main_page_list()


class ChannelAboutView(generics.RetrieveAPIView):
    """API endpoint to get info about channel.

    Supports caching. Cache available in 15 minutes.

    Example: /api/v1/c/henwixchannel/about

    """

    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseChannelAboutService = container.resolve(BaseChannelAboutService)

    def get_queryset(self):
        return self.service.get_channel_about_list()

    @method_decorator(cache_page(60 * 15, key_prefix='channel_about'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SubscriptionAPIView(viewsets.GenericViewSet):
    queryset = SubscriptionItem.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = get_container()
        self.service: BaseSubscriptionService = container.resolve(BaseSubscriptionService)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'to': {
                        'type': 'string',
                        'description': "'slug' field from channel instance to subscribe",
                        'example': 'henwix',
                    },
                },
                'required': ['to'],
            },
        },
        responses={
            200: OpenApiTypes.OBJECT,
            201: OpenApiTypes.OBJECT,
            204: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[OpenApiExample("Example: sub to 'henwix' channel", value={'to': 'henwix'}, request_only=True)],
    )
    @action(methods=['post'], url_path='subscribe', detail=False)
    def subscribe(self, request):
        """API endpoint to subscribe.

        JSON-body parameters: 'slug' - channel's slug to subscribe
        Example: api/v1/subscription/subscribe/

        """

        result = self.service.subscribe(user=request.user, channel_slug=request.data.get('to'))
        return Response(result, status.HTTP_201_CREATED)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'to': {
                        'type': 'string',
                        'description': "'slug' field from channel's instance to unsubscribe",
                        'example': 'henwix',
                    },
                },
                'required': ['to'],
            },
        },
        responses={
            204: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[OpenApiExample("Example: unsub from 'henwix' channel", value={'to': 'henwix'}, request_only=True)],
    )
    @action(methods=['post'], url_path='unsubscribe', detail=False)
    def unsubscribe(self, request):
        """API endpoint to unsubscribe.

        JSON-body parameters: 'to' - channel's slug to unsubscribe
        Example: api/v1/subscription/unsubscribe/

        """

        result = self.service.unsubscribe(user=request.user, channel_slug=request.data.get('to'))
        return Response(result, status.HTTP_204_NO_CONTENT)
