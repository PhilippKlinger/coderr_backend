from rest_framework.permissions import BasePermission

class IsReviewerOrReadOnly(BasePermission):
    """
    Erlaubt nur dem Ersteller (reviewer), die Bewertung zu ändern/löschen.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.reviewer == request.user
