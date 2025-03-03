from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from .models import Channel
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import OuterRef, Prefetch, Subquery, Count, Q
from apps.videos.models import Video
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from . import serializers

# Create your views here.

class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for detail, update and delete 'Channel' instances.
    If the request method is DELETE, related/associated 'User' will also be deleted.
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.method == "DELETE":
            return self.request.user

        return get_object_or_404(self.get_queryset(), user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with caching.
        """
        
        cache_key = f"retrieve_channel_{self.request.user.pk}"

        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)
        
        response = super().retrieve(request, *args, **kwargs)
        cache.set(
            key=cache_key,
            value=response.data,
            timeout=60*15
        )
        return response

class ChannelMainView(generics.RetrieveAPIView):
    """
    API endpoint to get channel main page. Main page includes info about channel and last public 5 videos.
    Example: /api/v1/c/henwixchannel
    """

    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"
    throttle_scope = 'channel'

    def get_queryset(self):
        second_query = (
            Video.objects.select_related("author")
            .filter(author__slug=OuterRef("author__slug"), status=Video.VideoStatus.PUBLIC)
            .values("pk")[:5]
        )

        queryset = Channel.objects.all().prefetch_related(
            Prefetch("videos", Video.objects.filter(pk__in=Subquery(second_query)).annotate(views_count=Count("views")))
        )
        return queryset


class ChannelAboutView(generics.RetrieveAPIView):
    """
    API endpoint to get info about channel.
    Supports caching. Cache available in 15 minutes.
    Example: /api/v1/c/henwixchannel/about/
    """

    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            Channel.objects.all()
            .select_related("user")
            .annotate(
                total_views=Count("videos__views"),
                total_videos=Count("videos", filter=Q(videos__status=Video.VideoStatus.PUBLIC), distinct=True),
                total_subs=Count("followers"),
            )
        )
        return queryset
    
    @method_decorator(cache_page(60*15, key_prefix="channel_about"))
    def retrieve(self, request, *args, **kwargs):
        """
        Custom 'retrieve' method with @cache_page decorator caching.
        """

        return super().retrieve(request, *args, **kwargs)