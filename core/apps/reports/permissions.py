from rest_framework import permissions


class IsStaffOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_authenticated:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
