from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerUser(BasePermission):
    """
    Erlaubt GET, HEAD, OPTIONS für alle.
    Schreibzugriff nur für authentifizierte Nutzer mit Profiltyp 'customer'.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.type == "customer"
        )


class IsOrderOwnerOrReadOnly(BasePermission):
    """
    PATCH nur für business_user,
    GET für beide Beteiligten,
    DELETE für Admins.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.customer_user == request.user or obj.business_user == request.user
        if request.method in ["PATCH", "PUT"]:
            return obj.business_user == request.user
        if request.method == "DELETE":
            return request.user.is_staff  # Nur Admin darf löschen!
        return False