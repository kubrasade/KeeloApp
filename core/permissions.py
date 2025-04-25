from rest_framework import permissions
from django.core.exceptions import PermissionDenied
from .enums import UserType

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsDietitian(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == UserType.DIETITIAN)

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == UserType.CLIENT)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == UserType.ADMIN)

class IsVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'is_verified') and request.user.is_verified)

class IsActiveUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)

class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id

class IsDietitianOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'user_type'):
            return False
        return request.user.user_type in [UserType.DIETITIAN, UserType.ADMIN]

class IsOwnerDietitianOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'user_type') and request.user.user_type == UserType.ADMIN:
            return True
        if hasattr(request.user, 'user_type') and request.user.user_type == UserType.DIETITIAN:
            if hasattr(obj, 'client') and hasattr(obj.client, 'dietitian'):
                return obj.client.dietitian == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        return False

class DietPlanPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'user_type'):
            return False
        if request.user.user_type == UserType.ADMIN:
            return True
        if request.method in ['POST', 'PUT', 'PATCH'] and request.user.user_type == UserType.DIETITIAN:
            return True
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == UserType.ADMIN:
            return True
        if request.user.user_type == UserType.DIETITIAN and hasattr(obj, 'dietitian'):
            return obj.dietitian == request.user
        if request.user.user_type == UserType.CLIENT and hasattr(obj, 'client'):
            return obj.client == request.user and request.method in permissions.SAFE_METHODS
        return False

class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-Key')
        return bool(api_key)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        elif hasattr(obj, 'client'):
            return obj.client == request.user or request.user.is_staff
        return request.user.is_staff

class IsProfileOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff or
            (hasattr(obj, 'user') and obj.user == request.user)
        )