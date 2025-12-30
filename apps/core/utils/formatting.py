# core/utils/formatting.py
"""
Date/time formatting utilities sesuai settings.py format.
"""
from django.conf import settings

from .datetime import to_jakarta_time


def format_datetime(dt, format_type='full'):
    """
    Format datetime sesuai settings.py format.
    
    Args:
        dt (datetime): Datetime to format
        format_type (str): 'full', 'full_day', 'short', 'short_day'
    
    Returns:
        str: Formatted datetime
    
    Examples:
        >>> dt = now()
        >>> format_datetime(dt, 'full')         # "30/12/2025 15:30:00"
        >>> format_datetime(dt, 'full_day')     # "Senin, 30/12/2025 15:30:00"
        >>> format_datetime(dt, 'short')        # "30/12 15:30"
        >>> format_datetime(dt, 'short_day')    # "Sen, 30/12 15:30"
    """
    if not dt:
        return "-"
    
    # Convert ke Jakarta timezone
    jakarta_dt = to_jakarta_time(dt)
    
    format_map = {
        'full': settings.DATETIME_FORMAT,
        'full_day': settings.DATETIME_FORMAT_DAY,
        'short': settings.SHORT_DATETIME_FORMAT,
        'short_day': settings.SHORT_DATETIME_FORMAT_DAY,
    }
    
    format_str = format_map.get(format_type, settings.DATETIME_FORMAT)
    return jakarta_dt.strftime(_convert_django_format(format_str))


def format_date(dt, format_type='full'):
    """
    Format date sesuai settings.py format.
    
    Args:
        dt (date/datetime): Date to format
        format_type (str): 'full', 'full_day', 'short', 'short_day'
    
    Returns:
        str: Formatted date
    
    Examples:
        >>> dt = today()
        >>> format_date(dt, 'full')         # "30/12/2025"
        >>> format_date(dt, 'full_day')     # "Senin, 30/12/2025"
        >>> format_date(dt, 'short')        # "30/12/25"
        >>> format_date(dt, 'short_day')    # "Sen, 30/12/25"
    """
    if not dt:
        return "-"
    
    format_map = {
        'full': settings.DATE_FORMAT,
        'full_day': settings.DATE_FORMAT_DAY,
        'short': settings.SHORT_DATE_FORMAT,
        'short_day': settings.SHORT_DATE_FORMAT_DAY,
    }
    
    format_str = format_map.get(format_type, settings.DATE_FORMAT)
    return dt.strftime(_convert_django_format(format_str))


def format_time(dt):
    """
    Format time sesuai settings.py format.
    
    Args:
        dt (datetime): Datetime to format
    
    Returns:
        str: Formatted time
    
    Examples:
        >>> dt = now()
        >>> format_time(dt)  # "15:30:00"
    """
    if not dt:
        return "-"
    
    jakarta_dt = to_jakarta_time(dt)
    return jakarta_dt.strftime(_convert_django_format(settings.TIME_FORMAT))


def _convert_django_format(django_format):
    """
    Convert Django date format ke Python strftime format.
    
    Django uses PHP-style formats (d/m/Y), Python uses % codes (%d/%m/%Y)
    """
    # Mapping Django format ke Python strftime
    conversions = {
        'd': '%d',   # Day 01-31
        'm': '%m',   # Month 01-12
        'Y': '%Y',   # Year 4 digits
        'y': '%y',   # Year 2 digits
        'H': '%H',   # Hour 00-23
        'i': '%M',   # Minute 00-59
        's': '%S',   # Second 00-59
        'l': '%A',   # Full day name (Senin)
        'D': '%a',   # Short day name (Sen)
    }
    
    result = django_format
    for django_code, python_code in conversions.items():
        result = result.replace(django_code, python_code)
    
    return result