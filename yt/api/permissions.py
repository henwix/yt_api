from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return hasattr(request.user, 'channel') and request.user.channel == obj.author
    

class IsAdminOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return hasattr(request.user, 'channel')
 
        return request.user.is_staff

        
        