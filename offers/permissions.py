from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessUser(BasePermission):
    """
    Erlaubt nur authentifizierten Business-Usern Schreibrechte.
    Leserechte sind für alle (AllowAny).
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
    Nur der Ersteller darf PATCH oder DELETE auf ein Angebot ausführen.
    GET ist für alle erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.user == request.user
            )
        )
