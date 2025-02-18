from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets
from .models import Channel, Video
from . import serializers
from .permissions import IsAuthorOrReadOnly, IsAdminOrAuthenticated
from rest_framework import permissions
from django.db.models import Count
from django.db.models import Prefetch


class CustomUserViewSet(UserViewSet):
    """
    Customized UserViewSet from Djoser: queryset attr has been changed to add prefetch_related('channel')
    """

    queryset = get_user_model().objects.all().prefetch_related("channel")


class ChannelRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Channel view for instance detail and update info.
    [!] If the request method is DELETE, related/associated user will also be deleted
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.method == "DELETE":
            return self.request.user

        return get_object_or_404(self.get_queryset(), user=self.request.user)


class ChannelMainView(generics.RetrieveAPIView):
    """
    Channel main page view
    """

    queryset = Channel.objects.all().prefetch_related(
        Prefetch("videos", Video.objects.filter(status=Video.VideoStatus.PUBLIC))
    )
    serializer_class = serializers.ChannelAndVideosSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"


class ChannelAboutView(generics.RetrieveAPIView):
    """
    Channel about info view
    """

    queryset = (
        Channel.objects.all()
        .select_related("user")
        .prefetch_related("videos")
        .annotate(total_views=Count("videos__views"), total_videos=Count("videos"), total_subs=Count("followers"))
    )
    serializer_class = serializers.ChannelAboutSerializer
    lookup_url_kwarg = "slug"
    lookup_field = "slug"


class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VideoSerializer
    lookup_field = "video_id"
    lookup_url_kwarg = "video_id"

    def get_queryset(self):
        if self.request.method == "GET":
            return Video.objects.select_related("author").all().annotate(likes_count=Count("likes"))

        return Video.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [IsAdminOrAuthenticated()]
        
        return [IsAuthorOrReadOnly()]

