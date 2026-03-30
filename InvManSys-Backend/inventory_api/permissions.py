from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Managers & Admins get full access
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'manager'):
            return True
        
        # Staff can view and edit (PUT/PATCH), but NOT create or delete
        if hasattr(request.user, 'profile') and request.user.profile.role == 'staff':
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH']

        # Default User role: Read-only
        return request.method in permissions.SAFE_METHODS