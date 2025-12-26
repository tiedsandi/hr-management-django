from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model.
    
    Jabatan/Role diatur via Django Groups (BUKAN field di model):
    - HR Admin: Full access
    - Manager: Division-level access  
    - Staff: Own data access only
    """
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='ID karyawan unik (contoh: EMP001, EMP002)'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        help_text='Nomor telepon karyawan'
    )
    division = models.ForeignKey(
        'Division',  # String reference karena sama app
        on_delete=models.PROTECT,
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
    
    # Face Recognition Fields
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
        help_text='Face encoding data untuk face recognition (auto-generated)'
    )

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name() or self.username}"

    def get_role_display(self):
        """
        Get jabatan dari Group pertama.
        Example: 'HR Admin', 'Manager', 'Staff'
        """
        group = self.groups.first()
        return group.name if group else "Employee"
    
    @property
    def has_face_photos(self):
        """Check apakah sudah upload semua foto wajah (3 foto)"""
        return all([
            self.face_photo_front,
            self.face_photo_left,
            self.face_photo_right
        ])
    
    @property
    def is_hr_admin(self):
        """Check apakah user adalah HR Admin"""
        return self.groups.filter(name='HR Admin').exists()
    
    @property
    def is_manager(self):
        """Check apakah user adalah Manager"""
        return self.groups.filter(name='Manager').exists()
    
    @property
    def is_staff_employee(self):
        """Check apakah user adalah Staff"""
        return self.groups.filter(name='Staff').exists()