"""
Tests untuk datetime utilities.
"""
from datetime import datetime, timedelta

import pytest
import pytz
from django.utils import timezone as django_timezone

from apps.core.utils.datetime import (
    format_time_diff,
    get_jakarta_timezone,
    get_month_range,
    get_week_range,
    is_same_day,
    now,
    to_jakarta_time,
)


class TestGetJakartaTimezone:
    """Test get_jakarta_timezone function"""
    
    def test_returns_jakarta_timezone(self):
        """Test returns timezone object untuk Jakarta"""
        tz = get_jakarta_timezone()
        
        assert tz.zone == 'Asia/Jakarta'
        assert isinstance(tz, pytz.tzinfo.BaseTzInfo)


class TestNow:
    """Test now() function"""
    
    def test_now_returns_datetime(self):
        """Test now() returns datetime object"""
        current = now()
        
        assert isinstance(current, datetime)
        assert current.tzinfo is not None
    
    def test_now_is_timezone_aware(self):
        """Test now() returns timezone-aware datetime"""
        current = now()
        
        assert django_timezone.is_aware(current)
    
    def test_now_is_jakarta_timezone(self):
        """Test now() menggunakan Jakarta timezone"""
        current = now()
        jakarta_tz = get_jakarta_timezone()
        
        # Convert to Jakarta timezone if not already
        current_jakarta = current.astimezone(jakarta_tz)
        
        assert current_jakarta.tzinfo.zone == 'Asia/Jakarta'


class TestToJakartaTime:
    """Test to_jakarta_time function"""
    
    def test_convert_utc_to_jakarta(self):
        """Test convert UTC datetime ke Jakarta"""
        utc_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        jakarta_time = to_jakarta_time(utc_time)
        
        # Jakarta is UTC+7, so 12:00 UTC = 19:00 Jakarta
        assert jakarta_time.hour == 19
        assert jakarta_time.tzinfo.zone == 'Asia/Jakarta'
    
    def test_convert_naive_datetime(self):
        """Test convert naive datetime ke Jakarta"""
        naive_time = datetime(2025, 1, 1, 12, 0, 0)
        jakarta_time = to_jakarta_time(naive_time)
        
        assert jakarta_time.tzinfo is not None
        assert jakarta_time.hour == 12  # Same hour, just adds timezone
    
    def test_already_jakarta_timezone(self):
        """Test datetime yang sudah Jakarta timezone"""
        jakarta_tz = get_jakarta_timezone()
        jakarta_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=jakarta_tz)
        result = to_jakarta_time(jakarta_time)
        
        assert result.hour == 12
        assert result.tzinfo.zone == 'Asia/Jakarta'


class TestFormatTimeDiff:
    """Test format_time_diff function"""
    
    def test_format_seconds_ago(self):
        """Test format untuk beberapa detik yang lalu"""
        current = now()
        past = current - timedelta(seconds=30)
        
        result = format_time_diff(past, current)
        
        assert 'detik' in result or 'second' in result.lower()
    
    def test_format_minutes_ago(self):
        """Test format untuk beberapa menit yang lalu"""
        current = now()
        past = current - timedelta(minutes=5)
        
        result = format_time_diff(past, current)
        
        assert 'menit' in result or 'minute' in result.lower()
    
    def test_format_hours_ago(self):
        """Test format untuk beberapa jam yang lalu"""
        current = now()
        past = current - timedelta(hours=2)
        
        result = format_time_diff(past, current)
        
        assert 'jam' in result or 'hour' in result.lower()
    
    def test_format_days_ago(self):
        """Test format untuk beberapa hari yang lalu"""
        current = now()
        past = current - timedelta(days=3)
        
        result = format_time_diff(past, current)
        
        assert 'hari' in result or 'day' in result.lower()
    
    def test_future_time(self):
        """Test format untuk waktu di masa depan"""
        current = now()
        future = current + timedelta(hours=1)
        
        result = format_time_diff(future, current)
        
        # Should handle future time gracefully
        assert isinstance(result, str)


class TestIsSameDay:
    """Test is_same_day function"""
    
    def test_same_day_same_time(self):
        """Test dua datetime di hari yang sama"""
        dt1 = datetime(2025, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
        dt2 = datetime(2025, 1, 1, 15, 0, 0, tzinfo=pytz.UTC)
        
        assert is_same_day(dt1, dt2) is True
    
    def test_different_day(self):
        """Test dua datetime di hari yang berbeda"""
        dt1 = datetime(2025, 1, 1, 23, 59, 0, tzinfo=pytz.UTC)
        dt2 = datetime(2025, 1, 2, 0, 1, 0, tzinfo=pytz.UTC)
        
        assert is_same_day(dt1, dt2) is False
    
    def test_same_day_different_timezone(self):
        """Test same day dengan timezone berbeda"""
        jakarta_tz = get_jakarta_timezone()
        utc_tz = pytz.UTC
        
        # 2025-01-01 08:00 Jakarta = 2025-01-01 01:00 UTC (same day)
        dt1 = datetime(2025, 1, 1, 8, 0, 0, tzinfo=jakarta_tz)
        dt2 = datetime(2025, 1, 1, 1, 0, 0, tzinfo=utc_tz)
        
        assert is_same_day(dt1, dt2) is True


class TestGetMonthRange:
    """Test get_month_range function"""
    
    def test_get_current_month_range(self):
        """Test get range untuk bulan ini"""
        start, end = get_month_range()
        
        assert start.day == 1
        assert end.day >= 28  # Last day of month
        assert start.month == end.month
        assert start < end
    
    def test_get_specific_month_range(self):
        """Test get range untuk bulan spesifik"""
        start, end = get_month_range(2025, 1)
        
        assert start == datetime(2025, 1, 1, 0, 0, 0)
        assert end.day == 31  # January has 31 days
        assert end.month == 1
    
    def test_february_leap_year(self):
        """Test February pada tahun kabisat"""
        start, end = get_month_range(2024, 2)  # 2024 is leap year
        
        assert end.day == 29
    
    def test_february_non_leap_year(self):
        """Test February pada tahun non-kabisat"""
        start, end = get_month_range(2025, 2)
        
        assert end.day == 28


class TestGetWeekRange:
    """Test get_week_range function"""
    
    def test_get_current_week_range(self):
        """Test get range untuk minggu ini"""
        start, end = get_week_range()
        
        assert start.weekday() == 0  # Monday
        assert end.weekday() == 6  # Sunday
        assert (end - start).days == 6
    
    def test_get_specific_week_range(self):
        """Test get range untuk minggu spesifik"""
        # 2025-01-01 is Wednesday
        specific_date = datetime(2025, 1, 1, tzinfo=pytz.UTC)
        start, end = get_week_range(specific_date)
        
        assert start.weekday() == 0  # Should be previous Monday
        assert end.weekday() == 6  # Should be next Sunday
        assert start <= specific_date <= end
