from django.core.exceptions import ValidationError
import os
import re


def validate_image_file(file):
    """Validate image upload"""
    # Max size 5MB
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('File size cannot exceed 5MB')
    
    # Valid extensions
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError('Only JPG, JPEG, PNG allowed')


def validate_phone_number(value):
    """
    Validate Indonesian phone number.
    Format: 08xxxxxxxxxx atau 62xxxxxxxxxx
    """
    if not value:
        return
    
    # Remove non-numeric characters
    cleaned = re.sub(r'\D', '', value)
    
    # Check length
    if len(cleaned) < 10 or len(cleaned) > 15:
        raise ValidationError(
            'Nomor telepon harus 10-15 digit',
            code='invalid_length'
        )
    
    # Check prefix
    if not cleaned.startswith(('08', '62')):
        raise ValidationError(
            'Nomor telepon harus diawali 08 atau 62',
            code='invalid_prefix'
        )