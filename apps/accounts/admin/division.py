from django.contrib import admin
from django.utils.html import format_html

from apps.accounts.models import Division


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    """Admin untuk Division dengan hierarchical display"""
    list_display = [
        'get_hierarchy', 'code', 'name', 'level',
        'employee_count', 'total_employees', 'is_active'
    ]
    list_filter = ['level', 'is_active', 'parent']
    search_fields = ['name', 'code']
    ordering = ['level', 'code']
    
    fieldsets = [
        ('Basic Info', {
            'fields': ('name', 'code', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    ]
    
    def get_hierarchy(self, obj):
        """Display hierarchy dengan indentation"""
        indent = '—' * obj.level
        if indent:
            indent += ' '
        return format_html(
            '<span style="color: #666;">{}</span>{}',
            indent,
            obj.name
        )
    get_hierarchy.short_description = 'Division'
    
    def employee_count(self, obj):
        """Count employees di division ini saja"""
        count = obj.employee_count
        return format_html('<b>{}</b>', count)
    employee_count.short_description = 'Employees'
    
    def total_employees(self, obj):
        """Count employees including children"""
        count = obj.total_employee_count
        if count != obj.employee_count:
            return format_html(
                '<span style="color: #0066cc;">{}</span>',
                count
            )
        return count
    total_employees.short_description = 'Total (+ Children)'