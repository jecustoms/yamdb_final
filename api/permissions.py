from rest_framework import permissions


class UserIsOwnerOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Here moderator, admin and superuser have the same access
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if view.action in ['partial_update', 'destroy']:
            return (
                obj.author == request.user
                or request.user.is_staff
                or request.user.is_admin
                or request.user.is_moderator
            )
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Django admin and role admin have the same access
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class IsAdminOrDenied(permissions.BasePermission):
    """
    Django admin and role admin have the same access
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class PutNotAllowed(permissions.BasePermission):
    """
    PUT method not allowed.
    """
    message = 'Method is not allowed'

    def has_object_permission(self, request, view, obj):
        if view.action == 'update':
            return False
        return True
