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
    Nur der Kunde (customer_user) darf PATCH oder DELETE auf eine Bestellung ausführen.
    Lesezugriff ist für alle erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (obj.customer_user == request.user or obj.business_user == request.user)
        )
