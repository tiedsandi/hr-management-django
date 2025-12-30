"""
User ViewSet for API v2
Enhanced with additional features and improved responses
"""
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import UserDetailSerializerV2, UserListSerializerV2

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=['Users V2'],
        summary='[V2] List users with enhanced metadata',
        description='Get paginated list of users with additional fields like account age and online status',
    ),
    retrieve=extend_schema(
        tags=['Users V2'],
        summary='[V2] Get user detail with relationships',
        description='Get detailed user information including division hierarchy, statistics, and permissions',
    ),
)
class UserViewSetV2(viewsets.ReadOnlyModelViewSet):
    """
    API V2: Enhanced User ViewSet
    
    **What's New in V2:**
    - ✨ Additional metadata fields (account_age_days, is_online)
    - 🏢 Division hierarchy path in responses
    - 📊 Account statistics endpoint
    - 🔍 Enhanced filtering by division hierarchy
    - 📱 Better mobile-friendly response structure
    
    **Endpoints:**
    - GET /api/v2/accounts/users/ - List users with metadata
    - GET /api/v2/accounts/users/{id}/ - Get user detail with relationships
    - GET /api/v2/accounts/users/statistics/ - Get overall statistics
    - GET /api/v2/accounts/users/{id}/activity/ - Get user activity summary
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['username', 'email', 'created_at', 'employee_id']
    ordering = ['-created_at']
    filterset_fields = ['is_active', 'division']
    
    def get_queryset(self):
        """Get active users with optimized queries"""
        return User.objects.filter(
            is_active=True
        ).select_related(
            'division',
            'division__parent'
        ).prefetch_related(
            'groups',
            'user_permissions'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return UserDetailSerializerV2
        return UserListSerializerV2
    
    @extend_schema(
        tags=['Users V2'],
        summary='[V2] Get overall user statistics',
        description='Get aggregated statistics about users in the system',
        responses={200: OpenApiResponse(description='Statistics data')},
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall user statistics
        
        GET /api/v2/accounts/users/statistics/
        """
        from datetime import timedelta

        from django.db.models import Count, Q
        from django.utils import timezone
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Users created in last 30 days
        last_30_days = timezone.now() - timedelta(days=30)
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        
        # Users by division
        by_division = User.objects.filter(
            is_active=True,
            division__isnull=False
        ).values(
            'division__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'summary': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'new_users_last_30_days': new_users_30d,
            },
            'top_divisions': list(by_division),
            'generated_at': timezone.now(),
        })
    
    @extend_schema(
        tags=['Users V2'],
        summary='[V2] Get user activity summary',
        description='Get activity summary for a specific user',
        responses={200: OpenApiResponse(description='Activity data')},
    )
    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """
        Get user activity summary
        
        GET /api/v2/accounts/users/{id}/activity/
        """
        user = self.get_object()
        from django.utils import timezone
        
        account_age = (timezone.now() - user.date_joined).days
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'account_created': user.date_joined,
            'account_age_days': account_age,
            'last_login': user.last_login,
            'last_updated': user.updated_at,
            'activity_score': min(account_age * 10, 1000),  # Mock score for demo
            'status': 'active' if user.is_active else 'inactive',
        })
