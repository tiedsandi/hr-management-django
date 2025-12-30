# core/models/base.py
from django.conf import settings
from django.db import models

from apps.core.utils import now


class TimeStampedModel(models.Model):
    """
    Abstract base model with automatic timestamp tracking.
    
    Provides:
        - created_at: Auto-set on creation
        - updated_at: Auto-updated on save
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet with soft delete support."""
    
    def active(self):
        """Return only active (non-deleted) objects."""
        return self.filter(is_active=True)
    
    def deleted(self):
        """Return only soft-deleted objects."""
        return self.filter(is_active=False)
    
    def hard_delete(self):
        """Permanently delete all objects in queryset."""
        return super().delete()


class SoftDeleteModel(models.Model):
    """
    Abstract base model with soft delete support.
    
    Provides:
        - is_active: Flag untuk soft delete
        - deleted_at: Timestamp when deleted
        - deleted_by: User who deleted
        - delete(): Soft delete method
        - hard_delete(): Permanent delete
        - restore(): Restore deleted object
    
    Managers:
        - objects.active(): Get active objects
        - objects.deleted(): Get deleted objects
    """
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_deleted',
        editable=False
    )
    
    objects = models.Manager.from_queryset(SoftDeleteQuerySet)()
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False, user=None):
        """Soft delete: mark as inactive instead of removing from DB."""
        self.is_active = False
        self.deleted_at = now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by'])
    
    def hard_delete(self):
        """Permanently delete from database."""
        super().delete()
    
    def restore(self):
        """Restore soft-deleted object."""
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by'])


class AuditModel(TimeStampedModel, SoftDeleteModel):
    """
    Combined model with timestamp tracking and soft delete support.
    
    Inherits all features from TimeStampedModel and SoftDeleteModel.
    """
    class Meta:
        abstract = True