from django.db import models


class Division(models.Model):
    """
    Divisi/Department perusahaan.
    Contoh: IT, Finance, HR, Marketing
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nama divisi lengkap (IT Department, Finance)'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Kode unik divisi (IT, FIN, HR, MKT)'
    )
    description = models.TextField(
        blank=True,
        help_text='Deskripsi divisi'
    )
    head = models.ForeignKey(
        'User',  # String reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_divisions',
        help_text='Kepala divisi (Manager/Head)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Status aktif divisi'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Division'
        verbose_name_plural = 'Divisions'

    def __str__(self):
        return f"{self.id} :{self.code} - {self.name}"