from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrStuffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            or request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_moderator or request.user.is_admin)
        )
