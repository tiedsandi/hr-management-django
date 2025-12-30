# core/permissions/constants.py
"""
Centralized permission constants.

Usage:
    from core.permissions import PermissionCodes
    
    # Check permission
    if user.has_perm(PermissionCodes.VIEW_COMPANY_DASHBOARD):
        ...
    
    # In decorator
    @permission_required(PermissionCodes.APPROVE_LEAVE)
    def approve_leave_view(request):
        ...
"""


class PermissionCodes:
    """
    Centralized permission codenames to avoid typos.
    
    Format: app_label.codename
    """
    
    # ========== DASHBOARD ==========
    VIEW_COMPANY_DASHBOARD = 'core.view_company_dashboard'
    VIEW_DIVISION_DASHBOARD = 'core.view_division_dashboard'
    VIEW_OWN_DASHBOARD = 'core.view_own_dashboard'
    EXPORT_DASHBOARD_DATA = 'core.export_dashboard_data'
    
    # ========== ATTENDANCE ==========
    VIEW_OWN_ATTENDANCE = 'attendance.view_attendance'  # Django default
    ADD_OWN_ATTENDANCE = 'attendance.add_attendance'
    CHANGE_OWN_ATTENDANCE = 'attendance.change_attendance'
    DELETE_OWN_ATTENDANCE = 'attendance.delete_attendance'
    
    APPROVE_ATTENDANCE = 'core.approve_attendance'
    VIEW_ALL_ATTENDANCE_REPORT = 'core.view_all_attendance_report'
    VIEW_DIVISION_ATTENDANCE = 'core.view_division_attendance'
    
    # ========== LEAVE ==========
    VIEW_OWN_LEAVE = 'leave.view_leave'
    ADD_LEAVE_REQUEST = 'leave.add_leave'
    CHANGE_OWN_LEAVE = 'leave.change_leave'
    DELETE_OWN_LEAVE = 'leave.delete_leave'
    
    APPROVE_ALL_LEAVES = 'core.approve_all_leaves'
    APPROVE_DIVISION_LEAVES = 'core.approve_division_leaves'
    REJECT_LEAVE = 'core.reject_leave'
    CANCEL_APPROVED_LEAVE = 'core.cancel_approved_leave'
    
    # ========== REPORTS / ANALYTICS ==========
    EXPORT_ATTENDANCE_REPORT = 'core.export_attendance_report'
    EXPORT_LEAVE_REPORT = 'core.export_leave_report'
    EXPORT_PAYROLL_REPORT = 'core.export_payroll_report'
    VIEW_ANALYTICS = 'core.view_analytics'
    EXPORT_EMPLOYEE_DATA = 'core.export_employee_data'
    
    # ========== USERS / EMPLOYEES ==========
    VIEW_ALL_EMPLOYEES = 'core.view_all_employees'
    VIEW_DIVISION_EMPLOYEES = 'core.view_division_employees'
    MANAGE_EMPLOYEES = 'core.manage_employees'
    MANAGE_DIVISIONS = 'core.manage_divisions'


class PermissionGroups:
    """
    Permission groupings by role.
    Makes it easier to assign permissions to Groups.
    """
    
    # Staff: Own data only
    STAFF = [
        PermissionCodes.VIEW_OWN_DASHBOARD,
        PermissionCodes.VIEW_OWN_ATTENDANCE,
        PermissionCodes.ADD_OWN_ATTENDANCE,
        PermissionCodes.VIEW_OWN_LEAVE,
        PermissionCodes.ADD_LEAVE_REQUEST,
    ]
    
    # Manager: Division-level access
    MANAGER = STAFF + [
        PermissionCodes.VIEW_DIVISION_DASHBOARD,
        PermissionCodes.VIEW_DIVISION_ATTENDANCE,
        PermissionCodes.VIEW_DIVISION_EMPLOYEES,
        PermissionCodes.APPROVE_DIVISION_LEAVES,
        PermissionCodes.EXPORT_ATTENDANCE_REPORT,
    ]
    
    # HR Admin: Full access
    HR_ADMIN = MANAGER + [
        PermissionCodes.VIEW_COMPANY_DASHBOARD,
        PermissionCodes.EXPORT_DASHBOARD_DATA,
        PermissionCodes.APPROVE_ALL_LEAVES,
        PermissionCodes.APPROVE_ATTENDANCE,
        PermissionCodes.VIEW_ALL_ATTENDANCE_REPORT,
        PermissionCodes.EXPORT_LEAVE_REPORT,
        PermissionCodes.EXPORT_PAYROLL_REPORT,
        PermissionCodes.VIEW_ANALYTICS,
        PermissionCodes.VIEW_ALL_EMPLOYEES,
        PermissionCodes.MANAGE_EMPLOYEES,
        PermissionCodes.MANAGE_DIVISIONS,
    ]


# ========== HELPER FUNCTIONS ==========

def get_permission_display_name(permission_code):
    """
    Get human-readable permission name.
    
    Args:
        permission_code (str): Permission code (e.g., 'core.view_company_dashboard')
    
    Returns:
        str: Display name
    
    Examples:
        >>> get_permission_display_name(PermissionCodes.VIEW_COMPANY_DASHBOARD)
        'Can view company-wide dashboard'
    """
    from django.contrib.auth.models import Permission
    app_label, codename = permission_code.split('.')
    try:
        perm = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename
        )
        return perm.name
    except Permission.DoesNotExist:
        return codename.replace('_', ' ').title()


def user_has_any_permission(user, permission_codes):
    """
    Check if user has ANY of the given permissions.
    
    Args:
        user (User): User instance
        permission_codes (list): List of permission codes
    
    Returns:
        bool: True if user has at least one permission
    
    Examples:
        >>> perms = [PermissionCodes.VIEW_COMPANY_DASHBOARD, PermissionCodes.VIEW_DIVISION_DASHBOARD]
        >>> if user_has_any_permission(request.user, perms):
        ...     # User can view some dashboard
    """
    return any(user.has_perm(perm) for perm in permission_codes)


def user_has_all_permissions(user, permission_codes):
    """
    Check if user has ALL of the given permissions.
    
    Args:
        user (User): User instance
        permission_codes (list): List of permission codes
    
    Returns:
        bool: True if user has all permissions
    """
    return all(user.has_perm(perm) for perm in permission_codes)