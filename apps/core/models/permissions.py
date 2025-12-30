"""
Dummy permission models.
Tidak create table di database (managed=False).
"""
from django.db import models


class AppPermission(models.Model):
    """
    Consolidated permission model.
    All custom permissions in one place.
    """
    
    class Meta:
        managed = False
        default_permissions = ()
        verbose_name = 'Application Permission'
        verbose_name_plural = 'Application Permissions'
        
        permissions = [
            # ========== DASHBOARD ==========
            ("view_company_dashboard", "Can view company-wide dashboard"),
            ("view_division_dashboard", "Can view division dashboard"),
            ("view_own_dashboard", "Can view own dashboard only"),
            ("export_dashboard_data", "Can export dashboard data"),
            
            # ========== ATTENDANCE ==========
            ("approve_attendance", "Can approve attendance exceptions"),
            ("view_all_attendance_report", "Can view all attendance reports"),
            
            # ========== LEAVE ==========
            ("approve_all_leaves", "Can approve all leave requests"),
            ("reject_leave", "Can reject leave requests"),
            ("cancel_approved_leave", "Can cancel approved leaves"),
            
            # ========== REPORTS ==========
            ("export_attendance_report", "Can export attendance report"),
            ("export_leave_report", "Can export leave report"),
            ("export_payroll_report", "Can export payroll report"),
            ("view_analytics", "Can view analytics dashboard"),
        ]