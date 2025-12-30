# core/utils/datetime.py
"""
Datetime utilities dengan Jakarta timezone support.
"""
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.utils import timezone


def get_jakarta_timezone():
    """Get Jakarta timezone object"""
    return pytz.timezone(settings.TIME_ZONE)


def now():
    """
    Get current datetime di Jakarta timezone.
    
    Returns:
        datetime: Current datetime dengan timezone Jakarta
    
    Examples:
        >>> from core.utils.datetime import now
        >>> current_time = now()
        >>> print(current_time)  # 2025-12-30 15:30:00+07:00
    """
    return timezone.now()


def today():
    """
    Get today's date di Jakarta timezone.
    
    Returns:
        date: Today's date
    
    Examples:
        >>> from core.utils.datetime import today
        >>> current_date = today()
        >>> print(current_date)  # 2025-12-30
    """
    return timezone.now().date()


def make_aware(dt):
    """
    Convert naive datetime ke timezone-aware Jakarta datetime.
    
    Args:
        dt (datetime): Naive datetime
    
    Returns:
        datetime: Timezone-aware datetime
    
    Examples:
        >>> from datetime import datetime
        >>> naive_dt = datetime(2025, 12, 30, 15, 30)
        >>> aware_dt = make_aware(naive_dt)
        >>> print(aware_dt)  # 2025-12-30 15:30:00+07:00
    """
    if timezone.is_aware(dt):
        return dt
    
    jakarta_tz = get_jakarta_timezone()
    return timezone.make_aware(dt, jakarta_tz)


def to_jakarta_time(dt):
    """
    Convert any timezone datetime ke Jakarta timezone.
    
    Args:
        dt (datetime): Datetime dengan timezone apapun
    
    Returns:
        datetime: Datetime di Jakarta timezone
    
    Examples:
        >>> utc_time = datetime(2025, 12, 30, 8, 30, tzinfo=pytz.UTC)
        >>> jakarta_time = to_jakarta_time(utc_time)
        >>> print(jakarta_time)  # 2025-12-30 15:30:00+07:00
    """
    if not timezone.is_aware(dt):
        dt = make_aware(dt)
    
    jakarta_tz = get_jakarta_timezone()
    return dt.astimezone(jakarta_tz)


def start_of_day(dt=None):
    """
    Get start of day (00:00:00) di Jakarta timezone.
    
    Args:
        dt (datetime, optional): Date to process. Default: today
    
    Returns:
        datetime: Start of day
    
    Examples:
        >>> start = start_of_day()
        >>> print(start)  # 2025-12-30 00:00:00+07:00
    """
    if dt is None:
        dt = now()
    
    jakarta_tz = get_jakarta_timezone()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=jakarta_tz)


def end_of_day(dt=None):
    """
    Get end of day (23:59:59) di Jakarta timezone.
    
    Args:
        dt (datetime, optional): Date to process. Default: today
    
    Returns:
        datetime: End of day
    
    Examples:
        >>> end = end_of_day()
        >>> print(end)  # 2025-12-30 23:59:59+07:00
    """
    if dt is None:
        dt = now()
    
    jakarta_tz = get_jakarta_timezone()
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=jakarta_tz)


def days_ago(days):
    """
    Get datetime N days ago dari sekarang.
    
    Args:
        days (int): Number of days
    
    Returns:
        datetime: Datetime N days ago
    
    Examples:
        >>> week_ago = days_ago(7)
        >>> print(week_ago)
    """
    return now() - timedelta(days=days)


def days_from_now(days):
    """
    Get datetime N days dari sekarang.
    
    Args:
        days (int): Number of days
    
    Returns:
        datetime: Datetime N days from now
    
    Examples:
        >>> next_week = days_from_now(7)
        >>> print(next_week)
    """
    return now() + timedelta(days=days)


def is_today(dt):
    """
    Check apakah datetime adalah hari ini di Jakarta timezone.
    
    Args:
        dt (datetime): Datetime to check
    
    Returns:
        bool: True jika hari ini
    
    Examples:
        >>> is_today(now())  # True
    """
    if not timezone.is_aware(dt):
        dt = make_aware(dt)
    
    jakarta_dt = to_jakarta_time(dt)
    today_date = today()
    return jakarta_dt.date() == today_date


def get_month_range(year=None, month=None):
    """
    Get start dan end datetime untuk bulan tertentu.
    
    Args:
        year (int, optional): Year. Default: current year
        month (int, optional): Month. Default: current month
    
    Returns:
        tuple: (start_datetime, end_datetime)
    
    Examples:
        >>> start, end = get_month_range(2025, 12)
        >>> print(start)  # 2025-12-01 00:00:00+07:00
        >>> print(end)    # 2025-12-31 23:59:59+07:00
    """
    current = now()
    year = year or current.year
    month = month or current.month
    
    jakarta_tz = get_jakarta_timezone()
    
    # Start of month
    start = datetime(year, month, 1, 0, 0, 0, tzinfo=jakarta_tz)
    
    # End of month
    if month == 12:
        end = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=jakarta_tz) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=jakarta_tz) - timedelta(seconds=1)
    
    return start, end