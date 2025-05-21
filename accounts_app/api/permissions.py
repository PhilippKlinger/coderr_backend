from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    Allows access only to the profile owner for unsafe methods.
    Safe methods (GET, HEAD, OPTIONS) are allowed for any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object permissions. 
        Read-only for any authenticated user; write only for the owner.
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
