
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet

from apps.core.models.base import AuditModel

if TYPE_CHECKING:
    from apps.accounts.models.user import User

class Division(AuditModel):  
    """
    Divisi/Department dengan hierarchical structure.
    
    Structure:
    - Top level: parent=None (e.g., HR Department, IT Department)
    - Sub level: parent=Division (e.g., HR Manager, IT Development)
    - Child level: parent=Sub Division (e.g., HR Recruitment)
    """
    name = models.CharField(
        max_length=100,
        help_text='Nama divisi (HR Department, HR Manager, HR Recruitment)'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Kode unik divisi (HR, HR-MGR, HR-RECRUIT)'
    )
    description = models.TextField(
        blank=True,
        help_text='Deskripsi divisi'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text='Parent division (kosong jika top level)'
    )
    level = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Hierarchy level (0=top, 1=sub, 2=child, dst)'
    )

    class Meta:
        db_table = 'divisions'
        ordering = ['level', 'code']
        verbose_name = 'Division'
        verbose_name_plural = 'Divisions'
        unique_together = [['name', 'parent']]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.code} > {self.code} - {self.name}"
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate level based on parent"""
        if self.parent:
            # Prevent circular reference
            if self.parent == self:
                raise ValidationError("Division cannot be its own parent")
            
            # Calculate level
            self.level = self.parent.level + 1
            
            # Max depth limit (optional)
            if self.level > 5:
                raise ValidationError("Maximum hierarchy depth is 5 levels")
        else:
            self.level = 0
        
        super().save(*args, **kwargs)

    def active_children(self) -> QuerySet["Division"]:
        return self.children.active()

    def active_employees(self) -> QuerySet["User"]:
        return self.employees.filter(is_active=True)
    
    @property
    def full_path(self):
        """
        Get full path dari root ke division ini.
        Example: 'HR Department > HR Manager > HR Recruitment'
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def root(self):
        """Get root division (top level)"""
        if self.parent:
            return self.parent.root
        return self
    
    def get_ancestors(self):
        """Get all parent divisions (bottom to top)"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """Get all child divisions (recursive)"""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_siblings(self):
        """Get divisions dengan parent yang sama"""
        if self.parent:
            return Division.objects.filter(parent=self.parent).exclude(id=self.id)
        return Division.objects.filter(parent__isnull=True).exclude(id=self.id)
    
    @property
    def employee_count(self):
        """Count ACTIVE employees di division ini"""
        return self.employees.filter(is_active=True).count()
    
    @property
    def total_employee_count(self):
        """Count ACTIVE employees including children"""
        count = self.employee_count
        for child in self.children.filter(deleted_at__isnull=True):
            count += child.total_employee_count
        return count