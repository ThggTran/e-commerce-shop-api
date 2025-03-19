from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'

class IsSellerOrAdmin(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.role == 'seller' or request.user.role == 'admin')
