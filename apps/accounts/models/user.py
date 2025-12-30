from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.utils import now
from apps.core.validators import validate_email_domain, validate_phone_number


class User(AbstractUser):
    """
    Custom User Model with audit trail support.
    
    Role Management:
        - Roles managed via Django Groups (HR Admin, Manager, Staff)
        - Use user.is_hr_admin, user.is_manager, user.is_staff_employee
    
    Audit Trail:
        - created: date_joined (from AbstractUser)
        - updated: updated_at (custom)
        - deleted: deleted_at, deleted_by (soft delete support)
    
    Face Recognition:
        - 3 photos required: front, left, right
        - face_encoding auto-generated (read-only)
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]

    # ========== EMPLOYEE INFO ==========
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='ID karyawan unik (contoh: EMP0001, EMP0002)'
    )
    email = models.EmailField(
        unique=True, 
        validators=[validate_email_domain]
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[validate_phone_number],
        help_text='Nomor telepon karyawan (08xxx atau 62xxx)'
    )
    division = models.ForeignKey(
        'Division',
        on_delete=models.PROTECT,  # Prevent accidental deletion
        related_name='employees',
        null=True,
        blank=True,
        help_text='Divisi karyawan'
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text='Tanggal mulai bekerja'
    )
    type_of_employment = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text='Jenis kepegawaian'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,  # Add index for filtering
        help_text='Status kepegawaian'
    )
    
    face_photo_front = models.ImageField(
        upload_to='faces/front/%Y/%m/',
        null=True,
        blank=True,
        help_text='Foto wajah tampak depan'
    )
    face_photo_left = models.ImageField(
        upload_to='faces/left/%Y/%m/',
        null=True,
        blank=True,
        help_text='Foto wajah tampak kiri'
    )
    face_photo_right = models.ImageField(
        upload_to='faces/right/%Y/%m/',
        null=True,
        blank=True,
        help_text='Foto wajah tampak kanan'
    )
    face_encoding = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        help_text='Face encoding data untuk face recognition (auto-generated)'
    )
    
    # ========== AUDIT FIELDS ==========
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Soft delete timestamp'
    )
    deleted_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_deleted',
        editable=False,
        help_text='User who deleted this record'
    )

    class Meta:
        db_table = 'users'
        ordering = ['employee_id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
        indexes = [
            models.Index(fields=['employee_id'], name='idx_employee_id'),
            models.Index(fields=['status', 'is_active'], name='idx_status_active'),
            models.Index(fields=['division', 'is_active'], name='idx_division_active'),
        ]
        
        permissions = [
            ("view_all_employees", "Can view all employees"),
            ("view_division_employees", "Can view division employees only"),
            ("manage_employee_face_data", "Can manage face recognition data"),
            ("bulk_import_employees", "Can bulk import employees"),
            ("export_employee_data", "Can export employee data"),
            ("reset_employee_password", "Can reset employee password"),
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name() or self.username}"
    
    # ========== SOFT DELETE METHODS ==========
    
    def soft_delete(self, user=None):
        """
        Soft delete user (set inactive instead of removing from DB).
        
        Args:
            user (User, optional): User who performed the deletion
        
        Examples:
            >>> employee.soft_delete(user=request.user)
            >>> # User is now inactive but still in DB
        """
        self.is_active = False
        self.deleted_at = now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by'])
    
    def restore(self):
        """
        Restore soft-deleted user.
        
        Examples:
            >>> employee.restore()
            >>> # User is now active again
        """
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by'])
    
    # ========== ROLE PROPERTIES ==========
    
    def get_role_display(self):
        """
        Get role name from first Group.
        
        Returns:
            str: Role name (e.g., 'HR Admin', 'Manager', 'Staff')
        
        Examples:
            >>> user.get_role_display()
            'HR Admin'
        """
        group = self.groups.first()
        return group.name if group else "Employee"
    
    @property
    def role(self):
        """Alias for get_role_display() untuk convenience"""
        return self.get_role_display()
    
    @property
    def is_hr_admin(self):
        """Check if user is HR Admin"""
        return self.groups.filter(name='HR Admin').exists()
    
    @property
    def is_manager(self):
        """Check if user is Manager"""
        return self.groups.filter(name='Manager').exists()
    
    @property
    def is_staff_employee(self):
        """Check if user is Staff"""
        return self.groups.filter(name='Staff').exists()
    
    # ========== FACE RECOGNITION PROPERTIES ==========
    
    @property
    def has_face_photos(self):
        """
        Check if all 3 face photos are uploaded.
        
        Returns:
            bool: True if all photos exist
        """
        return all([
            self.face_photo_front,
            self.face_photo_left,
            self.face_photo_right
        ])
    
    @property
    def has_complete_face_data(self):
        """
        Check if face photos + encoding are complete.
        
        Returns:
            bool: True if photos and encoding exist
        """
        return self.has_face_photos and self.face_encoding is not None
    
    def clear_face_data(self):
        """
        Clear all face recognition data (photos + encoding).
        Useful when re-enrolling or removing face data.
        
        Examples:
            >>> user.clear_face_data()
            >>> # All face photos and encoding removed
        """
        self.face_photo_front.delete(save=False)
        self.face_photo_left.delete(save=False)
        self.face_photo_right.delete(save=False)
        self.face_encoding = None
        self.save(update_fields=[
            'face_photo_front', 'face_photo_left', 
            'face_photo_right', 'face_encoding'
        ])
    
    # ========== EMPLOYEE INFO HELPERS ==========
    
    @property
    def full_name(self):
        """
        Get full name or username as fallback.
        
        Returns:
            str: Full name or username
        """
        return self.get_full_name() or self.username
    
    @property
    def is_employed(self):
        """Check if user is currently employed (active or on_leave)"""
        return self.status in ['active', 'on_leave']
    
    @property
    def is_terminated(self):
        """Check if user is terminated"""
        return self.status == 'terminated'
    
    def get_division_hierarchy(self):
        """
        Get full division hierarchy path.
        
        Returns:
            str: Division path (e.g., "HR Department > HR Manager > HR Recruitment")
        
        Examples:
            >>> user.get_division_hierarchy()
            'IT Department > IT Development'
        """
        if self.division:
            return self.division.full_path
        return "No Division"
    
    # ========== QUERYSETS (Custom Managers) ==========
    
    @classmethod
    def get_active_employees(cls):
        """
        Get all active employees (not deleted).
        
        Returns:
            QuerySet: Active users
        """
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def get_by_division(cls, division, include_children=False):
        """
        Get employees by division.
        
        Args:
            division (Division): Division to filter
            include_children (bool): Include child divisions
        
        Returns:
            QuerySet: Filtered employees
        
        Examples:
            >>> hr_dept = Division.objects.get(code='HR')
            >>> employees = User.get_by_division(hr_dept, include_children=True)
        """
        if include_children:
            divisions = [division] + division.get_descendants()
            return cls.objects.filter(
                is_active=True,
                division__in=divisions
            )
        return cls.objects.filter(
            is_active=True,
            division=division
        )
    
    @classmethod
    def get_by_role(cls, role_name):
        """
        Get employees by role (Group name).
        
        Args:
            role_name (str): Role name (e.g., 'HR Admin', 'Manager', 'Staff')
        
        Returns:
            QuerySet: Filtered employees
        
        Examples:
            >>> managers = User.get_by_role('Manager')
        """
        return cls.objects.filter(
            is_active=True,
            groups__name=role_name
        ).distinct()