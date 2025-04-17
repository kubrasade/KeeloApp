from django.db.models import QuerySet, Model
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from typing import Optional, Type, Any, Dict, List, Callable

User = get_user_model()


class QueryFilterService:
    @staticmethod
    def filter_queryset(
        queryset: QuerySet,
        request: HttpRequest,
        model_class: Type[Model],
        filters: Dict[str, Dict[str, Any]] = None,
        default_filters: Dict[str, Any] = None
    ) -> QuerySet:
        user = request.user
        
        if not user.is_authenticated:
            return queryset.none()
            
        if filters is None:
            filters = {}
            
        user_type = getattr(user, 'user_type', None)
        
        if user_type in filters:
            role_filters = filters[user_type]
            
            if callable(role_filters):
                return role_filters(queryset, user)
                
            return queryset.filter(**role_filters)
            
        if default_filters:
            if callable(default_filters):
                return default_filters(queryset, user)
            return queryset.filter(**default_filters)
            
        if hasattr(model_class, 'user') or hasattr(model_class, 'owner'):
            lookup_field = 'user' if hasattr(model_class, 'user') else 'owner'
            return queryset.filter(**{lookup_field: user})
            
        return queryset.none()
        
    @staticmethod
    def apply_common_filters(
        queryset: QuerySet,
        filters: Dict[str, Any] = None,
        exclude: Dict[str, Any] = None,
        order_by: List[str] = None,
        search_fields: List[str] = None,
        search_term: str = None,
        limit: int = None,
        prefetch_related: List[str] = None,
        select_related: List[str] = None
    ) -> QuerySet:
        if filters:
            queryset = queryset.filter(**filters)
            
        if exclude:
            queryset = queryset.exclude(**exclude)
            
        if search_fields and search_term:
            from django.db.models import Q
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_term})
            queryset = queryset.filter(query)
            
        if order_by:
            queryset = queryset.order_by(*order_by)
            
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
            
        if select_related:
            queryset = queryset.select_related(*select_related)
            
        if limit:
            queryset = queryset[:limit]
            
        return queryset
        
    @staticmethod
    def get_object_or_404(
        queryset: QuerySet,
        user: User,
        pk: int,
        permission_check: Callable[[Model, User], bool] = None
    ) -> Model:
        from django.shortcuts import get_object_or_404
        
        obj = get_object_or_404(queryset, pk=pk)
        
        if permission_check and not permission_check(obj, user):
            from django.http import Http404
            raise Http404("No permission to access this object")
            
        return obj 