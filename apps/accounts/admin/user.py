from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin untuk Custom User"""
    list_display = [
        'employee_id', 'username', 'get_full_name', 'email',
        'division', 'get_role', 'status', 'is_active'
    ]
    list_filter = [
        'is_active', 'is_staff', 'status',
        'type_of_employment', 'groups', 'division'
    ]
    search_fields = [
        'employee_id', 'username', 'email',
        'first_name', 'last_name'
    ]
    ordering = ['employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Employee Info', {
            'fields': (
                'employee_id', 'phone', 'division',
                'hire_date', 'type_of_employment', 'status'
            )
        }),
        ('Face Recognition', {
            'fields': (
                'face_photo_front', 'face_photo_left',
                'face_photo_right', 'face_encoding'
            ),
            'classes': ('collapse',) 
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Employee Info', {
            'fields': (
                'employee_id', 'email', 'phone',
                'division', 'hire_date'
            )
        }),
    )
    
    def get_role(self, obj):
        """Display role dari Groups"""
        return obj.get_role_display()
    get_role.short_description = 'Role'