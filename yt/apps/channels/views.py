import logging

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiTypes, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import CustomCursorPagination

from . import serializers
from .models import Channel, SubscriptionItem
from .repositories.channels import (
    ORMChannelAboutRepository,
    ORMChannelAvatarRepository,
    ORMChannelMainRepository,
    ORMChannelRepository,
    ORMChannelSubsRepository,
    ORMSubscriptionRepository,
)
from .services.channels import (
    CachedORMChannelService,
    ChannelAboutService,
    ChannelAvatarService,
    ChannelMainService,
    ChannelSubsService,
    SubscriptionService,
)

log = logging.getLogger(__name__)


class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for detail, update and delete 'Channel' instances.

    If the request method is DELETE, related/associated 'User' will also be deleted.

    Example: /api/v1/channel/
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CachedORMChannelService(
            repository=ORMChannelRepository(), serializer_class=self.serializer_class
        )

    def get_object(self):
        return self.service.repository.get_channel(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        channel_data = self.service.get_channel(request.user)
        return Response(channel_data)

    def destroy(self, request, *args, **kwargs):
        self.service.delete_channel(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChannelSubscribersView(generics.ListAPIView):
    """
    API endpoint to channel's subscribers listing.
    Supports cache for 15 minutes and Cursor pagination.
    Example: /api/v1/channel/subscribers/
    """

    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomCursorPagination
    queryset = SubscriptionItem.objects.all()

    def list(self, request, *args, **kwargs):
        """Custom list method to cache response."""

        cursor = request.query_params.get('c', '1')
        cache_key = f'cached_subs_{request.user.pk}_c_{cursor}'
        cached_data = cache.get(key=cache_key)

        if cached_data:
            return Response(cached_data)

        service = ChannelSubsService(repository=ORMChannelSubsRepository())
        qs = self.filter_queryset(service.get_subscriber_list(channel=request.user.channel))

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, 60 * 15)
            return response

        serializer = self.get_serializer(qs, many=True)
        response = Response(serializer.data)
        cache.set(cache_key, response.data, 60 * 15)
        return response


class ChannelAvatarDestroy(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        # TODO: add in celery
        service = ChannelAvatarService(repository=ORMChannelAvatarRepository())
        data, status = service.delete_avatar(request.user.channel)
        return Response(data, status)


class ChannelMainView(generics.RetrieveAPIView):
    """
    API endpoint to get channel main page. Main page includes info about channel and last 5 public videos.

    Example: /api/v1/c/henwixchannel
    """

    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'
    throttle_scope = 'channel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ChannelMainService(repository=ORMChannelMainRepository())

    def get_queryset(self):
        return self.service.get_channel_main_page_list()


class ChannelAboutView(generics.RetrieveAPIView):
    """
    API endpoint to get info about channel.

    Supports caching. Cache available in 15 minutes.

    Example: /api/v1/c/henwixchannel/about
    """

    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ChannelAboutService(repository=ORMChannelAboutRepository())

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
        self.service = SubscriptionService(repository=ORMSubscriptionRepository())

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'to': {
                        'type': 'string',
                        'description': "'slug' field from channel instance to subscribe",
                        'example': 'henwix',
                    }
                },
                'required': ['to'],
            }
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
        """
        API endpoint to subscribe.
        JSON-body parameters: 'slug' - channel's slug to subscribe
        Example: api/v1/subscription/subscribe/
        """

        data, status = self.service.subscribe(user=request.user, slug=request.data.get('to'))
        return Response(data, status)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'to': {
                        'type': 'string',
                        'description': "'slug' field from channel's instance to unsubscribe",
                        'example': 'henwix',
                    }
                },
                'required': ['to'],
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            201: OpenApiTypes.OBJECT,
            204: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[OpenApiExample("Example: unsub from 'henwix' channel", value={'to': 'henwix'}, request_only=True)],
    )
    @action(methods=['delete'], url_path='unsubscribe', detail=False)
    def unsubscribe(self, request):
        """
        API endpoint to unsubscribe.
        JSON-body parameters: 'slug' - channel's slug to unsubscribe
        Example: api/v1/subscription/unsubscribe/
        """

        data, status = self.service.unsubscribe(user=request.user, slug=request.data.get('to'))
        return Response(data, status)
