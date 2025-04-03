from rest_framework import permissions

from core.apps.videos.models import Video


class IsAuthenticatedOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'view':
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and obj.status != Video.VideoStatus.PRIVATE:
            return True

        return hasattr(request.user, 'channel') and (obj.author == request.user.channel or request.user.is_staff)


class IsAuthenticatedOrAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return hasattr(request.user, 'channel') and request.user.channel == obj.author
