from rest_framework import permissions

# --- CUSTOM PERMISSION CLASS ---
# Implements role-based access control (RBAC) based on the Profile roles
class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # 1. SUPERUSER & MANAGER ACCESS:
        # Check if the user is a Django superuser or has the 'manager' role in their profile.
        # These users are granted full CRUD (Create, Read, Update, Delete) permissions.
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'manager'):
            return True
        
        # 2. STAFF ACCESS:
        # Staff members are allowed to view data and modify existing records.
        # However, they are restricted from creating new records (POST) or deleting existing ones (DELETE).
        if hasattr(request.user, 'profile') and request.user.profile.role == 'staff':
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH']

        # 3. GENERAL USER / GUEST ACCESS:
        # For all other users (default 'user' role), only SAFE_METHODS are allowed.
        # SAFE_METHODS include read-only operations: GET, HEAD, and OPTIONS.
        return request.method in permissions.SAFE_METHODS