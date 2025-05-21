from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerUser(BasePermission):
    """
    Allows safe methods for any user.
    Write permissions are only granted to authenticated users with profile type 'customer'.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.type == "customer"
        )


class IsOrderOwnerOrReadOnly(BasePermission):
    """
    Allows PATCH only for the business user,
    GET for both related users,
    DELETE for admin users only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.customer_user == request.user or obj.business_user == request.user
        if request.method in ["PATCH", "PUT"]:
            return obj.business_user == request.user
        if request.method == "DELETE":
            return request.user.is_staff
        return False