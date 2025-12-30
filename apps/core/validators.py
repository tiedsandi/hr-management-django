import os
import re

from django.core.exceptions import ValidationError


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


def validate_email_domain(value):
    """
    Validate email with common domain checks.
    Ensures email has valid format and common domain.
    """
    if not value:
        return
    
    # Basic email format check (already handled by EmailField, but double check)
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError(
            'Format email tidak valid',
            code='invalid_format'
        )
    
    # Optional: Block disposable email domains
    disposable_domains = [
        'tempmail.com', 'throwaway.email', '10minutemail.com',
        'guerrillamail.com', 'mailinator.com', 'trashmail.com'
    ]
    
    domain = value.split('@')[1].lower()
    if domain in disposable_domains:
        raise ValidationError(
            'Email dari disposable domain tidak diperbolehkan',
            code='disposable_email'
        )


def validate_employee_id_format(value):
    """
    Validate employee ID format.
    Format: EMP followed by digits (e.g., EMP0001, EMP1234)
    """
    if not value:
        return
    
    # Pattern: EMP + 4 or more digits
    pattern = r'^EMP\d{4,}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Employee ID harus format EMPxxxx (contoh: EMP0001)',
            code='invalid_format'
        )