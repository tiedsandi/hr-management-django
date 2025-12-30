"""
Division API ViewSets
"""
from django.db.models import Count, Q
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

from apps.accounts.models import Division

from ..serializers import (
    DivisionCreateSerializer,
    DivisionDetailSerializer,
    DivisionListSerializer,
    DivisionUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Divisions'],
        summary='List divisions',
        description='Get list of all active divisions with pagination and filtering',
    ),
    create=extend_schema(
        tags=['Divisions'],
        summary='Create division',
        description='Create a new division/department',
    ),
    retrieve=extend_schema(
        tags=['Divisions'],
        summary='Get division detail',
        description='Get detailed information about a specific division',
    ),
    update=extend_schema(
        tags=['Divisions'],
        summary='Update division (full)',
        description='Update all fields of a division',
    ),
    partial_update=extend_schema(
        tags=['Divisions'],
        summary='Update division (partial)',
        description='Update specific fields of a division',
    ),
    destroy=extend_schema(
        tags=['Divisions'],
        summary='Delete division',
        description='Soft delete a division (if no children or employees)',
    ),
)
class DivisionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Division CRUD operations.
    
    Endpoints:
    - GET /api/v1/divisions/ - List all divisions
    - POST /api/v1/divisions/ - Create new division
    - GET /api/v1/divisions/{id}/ - Get division detail
    - PUT /api/v1/divisions/{id}/ - Update division (full)
    - PATCH /api/v1/divisions/{id}/ - Update division (partial)
    - DELETE /api/v1/divisions/{id}/ - Soft delete division
    
    Custom Actions:
    - GET /api/v1/divisions/tree/ - Get full hierarchy tree
    - GET /api/v1/divisions/{id}/children/ - Get children divisions
    - GET /api/v1/divisions/{id}/ancestors/ - Get ancestor divisions
    - GET /api/v1/divisions/{id}/employees/ - Get employees in division
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['code', 'name', 'level', 'created_at', 'employee_count']
    ordering = ['level', 'code']
    filterset_fields = ['level', 'parent']
    
    def get_queryset(self):
        """Get active divisions only with employee count annotation"""
        queryset = Division.objects.active().select_related('parent', 'deleted_by')
        
        # Filter by level if specified
        level = self.request.query_params.get('level')
        if level is not None:
            queryset = queryset.filter(level=level)
        
        # Filter top-level only
        if self.request.query_params.get('top_only') == 'true':
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DivisionListSerializer
        elif self.action in ['create']:
            return DivisionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DivisionUpdateSerializer
        else:
            return DivisionDetailSerializer
    
    def perform_destroy(self, instance):
        """Soft delete division"""
        from rest_framework.exceptions import ValidationError
        
        if instance.children.filter(deleted_at__isnull=True).exists():
            raise ValidationError(
                {'detail': 'Tidak dapat menghapus division yang memiliki sub-divisions aktif'}
            )
        
        if instance.employees.filter(is_active=True).exists():
            raise ValidationError(
                {'detail': 'Tidak dapat menghapus division yang memiliki employees aktif'}
            )
        
        # Soft delete using model's delete method
        instance.delete(user=self.request.user)
    
    @extend_schema(
        tags=['Divisions'],
        summary='Get division hierarchy tree',
        description='Get full hierarchical tree structure of all divisions',
        responses={200: DivisionListSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get full division hierarchy tree.
        
        GET /api/v1/divisions/tree/
        
        Returns nested structure of all divisions.
        """
        # Get all top-level divisions
        top_divisions = Division.objects.active().filter(parent__isnull=True)
        
        def build_tree(division):
            """Recursively build tree structure"""
            children = division.active_children()
            
            data = DivisionListSerializer(division).data
            if children.exists():
                data['children'] = [build_tree(child) for child in children]
            else:
                data['children'] = []
            
            return data
        
        tree_data = [build_tree(div) for div in top_divisions]
        
        return Response({
            'count': len(tree_data),
            'tree': tree_data
        })
    
    @extend_schema(
        tags=['Divisions'],
        summary='Get division children',
        description='Get immediate children divisions of a specific division',
        responses={200: DivisionListSerializer(many=True)},
    )
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        Get immediate children of a division.
        
        GET /api/v1/divisions/{id}/children/
        """
        division = self.get_object()
        children = division.active_children()
        
        serializer = DivisionListSerializer(children, many=True)
        return Response({
            'count': children.count(),
            'results': serializer.data
        })
    
    @extend_schema(
        tags=['Divisions'],
        summary='Get division ancestors',
        description='Get all ancestor divisions (parents up to root) of a specific division',
        responses={200: OpenApiResponse(description='List of ancestor divisions')},
    )
    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        """
        Get all ancestor divisions (parents up to root).
        
        GET /api/v1/divisions/{id}/ancestors/
        """
        division = self.get_object()
        ancestors = division.get_ancestors()
        
        data = [
            {
                'id': a.id,
                'code': a.code,
                'name': a.name,
                'level': a.level,
            }
            for a in ancestors
        ]
        
        return Response({
            'count': len(ancestors),
            'results': data
        })
    
    @extend_schema(
        tags=['Divisions'],
        summary='Get division employees',
        description='Get active employees in a specific division (optionally including children divisions)',
        parameters=[
            OpenApiParameter(
                name='include_children',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Include employees from child divisions',
                required=False,
                default=False,
            ),
        ],
        responses={200: OpenApiResponse(description='List of employees')},
    )
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """
        Get active employees in this division.
        
        GET /api/v1/divisions/{id}/employees/
        Query params:
        - include_children: true/false (default: false)
        """
        from apps.accounts.models import User
        
        division = self.get_object()
        include_children = request.query_params.get('include_children', 'false').lower() == 'true'
        
        if include_children:
            # Get employees from this division and all children
            division_ids = [division.id]
            descendants = division.get_descendants()
            division_ids.extend([d.id for d in descendants])
            
            employees = User.objects.filter(
                is_active=True,
                division_id__in=division_ids
            ).select_related('division')
        else:
            # Get employees from this division only
            employees = division.active_employees().select_related('division')
        
        # Simple employee data
        data = [
            {
                'id': emp.id,
                'employee_id': emp.employee_id,
                'username': emp.username,
                'full_name': emp.get_full_name(),
                'email': emp.email,
                'division': emp.division.name if emp.division else None,
            }
            for emp in employees
        ]
        
        return Response({
            'division': division.name,
            'include_children': include_children,
            'count': len(data),
            'results': data
        })
