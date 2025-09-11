from rest_framework import permissions

from core.apps.videos.models import (
    Playlist,
    Video,
)


class IsAuthorOrReadOnlyPlaylist(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['retrieve', 'videos']:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user_channel = getattr(request.user, 'channel') if hasattr(request.user, 'channel') else None

        if view.action in ['retrieve', 'videos'] and obj.status != Playlist.StatusChoices.PRIVATE:
            return True

        return user_channel and (user_channel.pk == obj.channel_id or request.user.is_staff)


class VideoIsAuthenticatedOrAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'view_create':
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and obj.status != Video.VideoStatus.PRIVATE:
            return True

        return hasattr(request.user, 'channel') and (obj.author == request.user.channel or request.user.is_staff)
