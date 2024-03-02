from rest_framework.permissions import BasePermission, SAFE_METHODS

class  IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow only admin users to modify objects.
    """

    def has_permission(self, request, view):
        # Allow read-only permissions for any request (GET, HEAD, OPTIONS).
        if request.method in SAFE_METHODS and request.user.is_authenticated:
            return True
        
        # Allow full permissions (GET, POST, PUT, DELETE) for admin users.
        if request.user.is_authenticated and request.user.is_staff:
            return True
        
        # For non-admin authenticated users, only allow read-only access.
        return False
