from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminAuthorOrReadOnly(BasePermission):
    """
    Проверка, является ли пользователь администратором,
    автором или модератором или только чтение.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (obj.author == request.user or request.user.is_superuser)
        )
