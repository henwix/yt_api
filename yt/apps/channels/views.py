from django.core.cache import cache
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiTypes, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import CustomCursorPagination
from apps.videos.models import Video

from . import serializers
from .models import Channel, SubscriptionItem


class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for detail, update and delete 'Channel' instances.
    If the request method is DELETE, related/associated 'User' will also be deleted.
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.method == 'DELETE':
            return self.request.user

        return get_object_or_404(self.get_queryset(), user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with caching.
        """

        cache_key = f'retrieve_channel_{self.request.user.pk}'

        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(key=cache_key, value=response.data, timeout=60 * 15)
        return response


class ChannelSubscribersView(generics.ListAPIView):
    """
    API endpoint to channel's subscribers listing.
    Supports cache for 15 minutes and Cursor pagination.
    Example: /api/v1/channel/subscribers/
    """

    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        return SubscriptionItem.objects.filter(subscribed_to=self.request.user.channel).select_related(
            'subscriber', 'subscribed_to'
        )

    def list(self, request, *args, **kwargs):
        """
        Custom list method to cache response.
        """

        cache_key = f'cached_subs_page_{request.user.pk}'
        cached_data = cache.get(key=cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 15)

        return response


class ChannelAvatarDestroy(APIView):
    def delete(self, request):
        channel = request.user.channel

        if not hasattr(channel, 'channel_avatar'):
            return Response({'error': 'Avatar does not exists'}, status=status.HTTP_404_NOT_FOUND)

        channel.channel_avatar.delete()
        channel.channel_avatar = None
        channel.save()

        return Response({'status': 'Success'}, status=status.HTTP_204_NO_CONTENT)


class ChannelMainView(generics.RetrieveAPIView):
    """
    API endpoint to get channel main page. Main page includes info about channel and last public 5 videos.
    Example: /api/v1/c/henwixchannel
    """

    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'
    throttle_scope = 'channel'

    def get_queryset(self):
        second_query = (
            Video.objects.select_related('author')
            .filter(author__slug=OuterRef('author__slug'), status=Video.VideoStatus.PUBLIC)
            .values('pk')[:5]
        )
        # FIXME: почему-то видео выдаются в странном порядке, только что сделал видео, оно выдаётся не последним, а 3м в списке, хотя должно первым. Название видео 'we'
        queryset = (
            Channel.objects.all()
            .annotate(subs_count=Count('followers', distinct=True))
            .prefetch_related(
                Prefetch(
                    'videos',
                    Video.objects.filter(pk__in=Subquery(second_query)).annotate(
                        views_count=Count('views', distinct=True)
                    ),
                )
            )
        )
        return queryset


class ChannelAboutView(generics.RetrieveAPIView):
    """
    API endpoint to get info about channel.
    Supports caching. Cache available in 15 minutes.
    Example: /api/v1/c/henwixchannel/about
    """

    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = (
            Channel.objects.all()
            .select_related('user')
            .annotate(
                total_views=Count('videos__views', distinct=True),
                total_videos=Count('videos', filter=Q(videos__status=Video.VideoStatus.PUBLIC), distinct=True),
                total_subs=Count('followers', distinct=True),
            )
        )
        return queryset

    @method_decorator(cache_page(60 * 15, key_prefix='channel_about'))
    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with @cache_page decorator caching.
        """

        return super().retrieve(request, *args, **kwargs)


class SubscriptionAPIView(viewsets.GenericViewSet):
    queryset = SubscriptionItem.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _sub_validation(self, request):
        subscriber = request.user.channel
        subscribed_to = get_object_or_404(Channel, slug=request.data.get('to'))

        if subscriber.pk == subscribed_to.pk:
            return (
                Response({'error': 'You cannot subscribe to yourself'}, status=status.HTTP_400_BAD_REQUEST),
                None,
                None,
            )

        return None, subscriber, subscribed_to

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

        error, subscriber, subscribed_to = self._sub_validation(request)
        if error:
            return error

        _, created = SubscriptionItem.objects.get_or_create(subscriber=subscriber, subscribed_to=subscribed_to)

        if created:
            return Response({'status': 'Success'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Already subscribed'}, status=status.HTTP_200_OK)

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
    @action(methods=['post'], url_path='unsubscribe', detail=False)
    def unsubscribe(self, request):
        """
        API endpoint to unsubscribe.
        JSON-body parameters: 'slug' - channel's slug to unsubscribe
        Example: api/v1/subscription/unsubscribe/
        """

        error, subscriber, subscribed_to = self._sub_validation(request)
        if error:
            return error

        deleted, _ = SubscriptionItem.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).delete()

        if deleted:
            return Response({'status': 'Success'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'error': 'Subscription does not exists'}, status=status.HTTP_404_NOT_FOUND)
