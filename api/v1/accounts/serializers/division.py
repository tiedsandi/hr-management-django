"""
Division API Serializers
"""
from rest_framework import serializers

from apps.accounts.models import Division


class DivisionListSerializer(serializers.ModelSerializer):
    """Serializer untuk list divisions (lightweight)"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Division
        fields = [
            'id',
            'code',
            'name',
            'parent',
            'parent_name',
            'level',
            'employee_count',
            'created_at',
        ]
        read_only_fields = ['id', 'level', 'created_at']
    
    def get_employee_count(self, obj):
        """Get employee count from model property"""
        return obj.employee_count


class DivisionDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail division (full info)"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    full_path = serializers.CharField(read_only=True)
    employee_count = serializers.SerializerMethodField()
    total_employee_count = serializers.SerializerMethodField()
    
    # Children divisions
    children = serializers.SerializerMethodField()
    
    # Ancestors (parents up to root)
    ancestors = serializers.SerializerMethodField()
    
    class Meta:
        model = Division
        fields = [
            'id',
            'code',
            'name',
            'description',
            'parent',
            'parent_name',
            'level',
            'full_path',
            'employee_count',
            'total_employee_count',
            'children',
            'ancestors',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'level',
            'full_path',
            'created_at',
            'updated_at',
        ]
    
    def get_employee_count(self, obj):
        """Get employee count from model property"""
        return obj.employee_count
    
    def get_total_employee_count(self, obj):
        """Get total employee count including children"""
        return obj.total_employee_count
    
    def get_children(self, obj):
        """Get immediate children only (not recursive)"""
        children = obj.active_children()
        return DivisionListSerializer(children, many=True).data
    
    def get_ancestors(self, obj):
        """Get all parent divisions"""
        ancestors = obj.get_ancestors()
        return [{'id': a.id, 'name': a.name, 'code': a.code, 'level': a.level} for a in ancestors]


class DivisionCreateSerializer(serializers.ModelSerializer):
    """Serializer untuk create division"""
    
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.filter(deleted_at__isnull=True),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Division
        fields = [
            'id',
            'code',
            'name',
            'description',
            'parent',
            'level',
            'created_at',
        ]
        read_only_fields = ['id', 'level', 'created_at']
    
    def validate_code(self, value):
        """Validate code format (uppercase, no spaces)"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                'Code harus alphanumeric (boleh dengan - atau _)'
            )
        return value.upper()
    
    def validate_parent(self, value):
        """Validate parent exists and not creating circular reference"""
        if value:
            # Check if parent exists and is active
            if value.deleted_at is not None:
                raise serializers.ValidationError('Parent division sudah dihapus')
            
            # Check depth limit
            if value.level >= 4:
                raise serializers.ValidationError(
                    'Maximum hierarchy depth adalah 5 levels'
                )
        
        return value


class DivisionUpdateSerializer(serializers.ModelSerializer):
    """Serializer untuk update division"""
    
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.filter(deleted_at__isnull=True),
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Division
        fields = [
            'id',
            'code',
            'name',
            'description',
            'parent',
            'level',
            'updated_at',
        ]
        read_only_fields = ['id', 'level', 'updated_at']
    
    def validate_code(self, value):
        """Validate code format"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                'Code harus alphanumeric (boleh dengan - atau _)'
            )
        return value.upper()
    
    def validate_parent(self, value):
        """Validate parent change doesn't create circular reference"""
        instance = self.instance
        
        if value:
            # Cannot set self as parent
            if value == instance:
                raise serializers.ValidationError('Division tidak bisa menjadi parent dari dirinya sendiri')
            
            # Cannot set child as parent (circular reference)
            descendants = instance.get_descendants()
            if value in descendants:
                raise serializers.ValidationError('Tidak bisa set child division sebagai parent')
            
            # Check if parent is active
            if value.deleted_at is not None:
                raise serializers.ValidationError('Parent division sudah dihapus')
            
            # Check depth after parent change
            if value.level >= 4:
                raise serializers.ValidationError('Maximum hierarchy depth adalah 5 levels')
        
        return value
