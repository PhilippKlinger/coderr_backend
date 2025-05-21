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
