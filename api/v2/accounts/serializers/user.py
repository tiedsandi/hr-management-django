"""
User Serializers for API v2
Enhanced with additional fields and improved structure
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializerV2(serializers.ModelSerializer):
    """
    V2: Enhanced user list with additional metadata
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    account_age_days = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'username',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'phone',
            'division_name',
            'is_active',
            'account_age_days',
            'is_online',
            'date_joined',
        ]
    
    def get_account_age_days(self, obj):
        """Calculate account age in days"""
        from django.utils import timezone
        delta = timezone.now() - obj.date_joined
        return delta.days
    
    def get_is_online(self, obj):
        """Mock online status - in real app, check last activity"""
        return obj.is_active  # Simplified for demo


class UserDetailSerializerV2(serializers.ModelSerializer):
    """
    V2: Detailed user info with relationships
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    division_info = serializers.SerializerMethodField()
    account_statistics = serializers.SerializerMethodField()
    permissions_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'username',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'phone',
            'status',
            'type_of_employment',
            'hire_date',
            'is_active',
            'division_info',
            'account_statistics',
            'permissions_summary',
            'date_joined',
            'updated_at',
        ]
    
    def get_division_info(self, obj):
        """Get division with hierarchy path"""
        if not obj.division:
            return None
        
        division = obj.division
        ancestors = division.get_ancestors()
        
        return {
            'id': division.id,
            'code': division.code,
            'name': division.name,
            'level': division.level,
            'hierarchy_path': ' > '.join([a.name for a in ancestors] + [division.name]),
            'employee_count': division.employee_count,
        }
    
    def get_account_statistics(self, obj):
        """Get user statistics"""
        from django.utils import timezone
        delta = timezone.now() - obj.date_joined
        
        return {
            'account_age_days': delta.days,
            'is_superuser': obj.is_superuser,
            'is_staff': obj.is_staff,
            'last_login': obj.last_login,
        }
    
    def get_permissions_summary(self, obj):
        """Get permissions summary"""
        return {
            'total_permissions': obj.user_permissions.count(),
            'groups': list(obj.groups.values_list('name', flat=True)),
            'is_admin': obj.is_superuser or obj.is_staff,
        }
