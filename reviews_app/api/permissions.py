from rest_framework.permissions import BasePermission

class IsReviewerOrReadOnly(BasePermission):
    """
    Custom permission to allow only the reviewer to update or delete a review.
    Read-only access for all authenticated users.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.reviewer == request.user

class IsCustomerUser(BasePermission):
    """
    Custom permission for Write-Only acces to profile "customer".
    """
    def has_permission(self, request, view):
        if request.method in ("POST", "PATCH", "PUT", "DELETE"):
            return (
                request.user.is_authenticated and
                hasattr(request.user, "profile") and
                request.user.profile.type == "customer"
            )
        return request.user.is_authenticated