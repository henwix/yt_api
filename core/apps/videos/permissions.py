from rest_framework import permissions

from core.apps.videos.models import Playlist


# list, retrieve, create, delete, put/update
class IsAuthorOrReadOnlyPlaylist(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user_channel = getattr(request.user, 'channel') if hasattr(request.user, 'channel') else None

        if obj.status == Playlist.StatusChoices.PRIVATE:
            return user_channel and (obj.channel == user_channel or request.user.is_staff)

        if view.action == 'retrieve':
            return True

        return user_channel and (user_channel == obj.channel or request.user.is_staff)
