from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to allow only Admin users to access view.
    """

    def has_permission(self, request, view):
        # Admins can create events
        if request.method == "POST":
            return request.user.is_authenticated and request.user.role == "Admin"
        return request.user.is_authenticated 


class IsRegularUser(BasePermission):
    """
    Custom permission to allow only regular users (not Admins) to access view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "User"