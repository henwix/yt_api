from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from rest_framework import generics
from .models import Channel
from . import serializers
from rest_framework import permissions


class CustomUserViewSet(UserViewSet):
    """
    Customized UserViewSet from Djoser: queryset attr has been changed to add prefetch_related('channel')
    """

    queryset = get_user_model().objects.all().prefetch_related('channel')


class ChannelDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Channel view for instance-detail and update
    """

    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.get_queryset().prefetch_related('videos'), user=self.request.user)
    

class VideoUploadView(generics.CreateAPIView):
    """
    Video-Upload view for creating new videos
    """

    serializer_class = serializers.VideoSerializer
    permission_classes = [permissions.IsAuthenticated]