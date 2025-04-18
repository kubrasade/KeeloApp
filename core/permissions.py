from rest_framework import permissions
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.conf import settings

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
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == 'DIETITIAN')
        
class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == 'CLIENT')

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'user_type') and request.user.user_type == 'ADMIN')

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
        return request.user.user_type in ['DIETITIAN', 'ADMIN']

class IsOwnerDietitianOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'user_type') and request.user.user_type == 'ADMIN':
            return True
            
        if hasattr(request.user, 'user_type') and request.user.user_type == 'DIETITIAN':
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
            
        if request.user.user_type == 'ADMIN':
            return True
            
        if request.method in ['POST', 'PUT', 'PATCH'] and request.user.user_type == 'DIETITIAN':
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
            
        return False
        
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'ADMIN':
            return True
            
        if request.user.user_type == 'DIETITIAN' and hasattr(obj, 'dietitian'):
            return obj.dietitian == request.user
            
        if request.user.user_type == 'CLIENT' and hasattr(obj, 'client'):
            return obj.client == request.user and request.method in permissions.SAFE_METHODS
            
        return False

class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
        return True 