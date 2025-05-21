from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessUser(BasePermission):
    """
    Allows write permissions only to authenticated business users.
    Read permissions are allowed for any request.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and hasattr(request.user, "profile")
                and request.user.profile.type == "business"
            )
        )


class IsOfferOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: Only the offer creator can update or delete the offer.
    Read-only access is allowed to anyone.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.user == request.user
            )
        )
