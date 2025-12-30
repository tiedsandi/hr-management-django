"""
Tests untuk formatting utilities.
"""
from datetime import datetime

import pytest
import pytz

from apps.core.utils.datetime import get_jakarta_timezone
from apps.core.utils.formatting import (
    format_currency,
    format_date,
    format_datetime,
    format_phone_number,
    format_time,
)


class TestFormatDatetime:
    """Test format_datetime function"""
    
    def test_format_full(self):
        """Test format datetime lengkap"""
        dt = datetime(2025, 12, 30, 15, 30, 45, tzinfo=pytz.UTC)
        result = format_datetime(dt, 'full')
        
        # Format: "30/12/2025 15:30:45"
        assert '30/12/2025' in result
        assert '15:30' in result or '22:30' in result  # Depends on timezone conversion
    
    def test_format_short(self):
        """Test format datetime pendek"""
        dt = datetime(2025, 12, 30, 15, 30, 0, tzinfo=pytz.UTC)
        result = format_datetime(dt, 'short')
        
        # Format: "30/12 15:30"
        assert '30/12' in result
        assert ':' in result  # Has time
    
    def test_format_none_datetime(self):
        """Test format dengan datetime None"""
        result = format_datetime(None)
        
        assert result == '-' or result == ''
    
    def test_format_with_day_name(self):
        """Test format dengan nama hari"""
        dt = datetime(2025, 12, 30, 15, 30, 0, tzinfo=pytz.UTC)
        result = format_datetime(dt, 'full_day')
        
        # Should include day name
        assert isinstance(result, str)
        assert len(result) > 10  # Longer than date only


class TestFormatDate:
    """Test format_date function"""
    
    def test_format_date_default(self):
        """Test format tanggal default"""
        dt = datetime(2025, 12, 30, 15, 30, 0, tzinfo=pytz.UTC)
        result = format_date(dt)
        
        # Format: "30/12/2025"
        assert '30' in result
        assert '12' in result
        assert '2025' in result
    
    def test_format_date_short(self):
        """Test format tanggal pendek"""
        dt = datetime(2025, 12, 30, 15, 30, 0, tzinfo=pytz.UTC)
        result = format_date(dt, 'short')
        
        # Format: "30/12"
        assert '30/12' in result
        assert '2025' not in result  # Short format excludes year
    
    def test_format_none_date(self):
        """Test format dengan date None"""
        result = format_date(None)
        
        assert result == '-' or result == ''


class TestFormatTime:
    """Test format_time function"""
    
    def test_format_time_default(self):
        """Test format waktu default"""
        dt = datetime(2025, 12, 30, 15, 30, 45, tzinfo=pytz.UTC)
        result = format_time(dt)
        
        # Format: "15:30:45" or "22:30:45" (Jakarta)
        assert ':' in result
        parts = result.split(':')
        assert len(parts) in [2, 3]  # HH:MM or HH:MM:SS
    
    def test_format_time_no_seconds(self):
        """Test format waktu tanpa detik"""
        dt = datetime(2025, 12, 30, 15, 30, 45, tzinfo=pytz.UTC)
        result = format_time(dt, include_seconds=False)
        
        # Format: "15:30"
        parts = result.split(':')
        assert len(parts) == 2
    
    def test_format_none_time(self):
        """Test format dengan time None"""
        result = format_time(None)
        
        assert result == '-' or result == ''


class TestFormatCurrency:
    """Test format_currency function"""
    
    def test_format_currency_default(self):
        """Test format currency dengan Rupiah"""
        result = format_currency(1000000)
        
        # Format: "Rp 1.000.000"
        assert 'Rp' in result
        assert '1.000.000' in result or '1,000,000' in result
    
    def test_format_currency_zero(self):
        """Test format currency dengan nilai 0"""
        result = format_currency(0)
        
        assert 'Rp' in result
        assert '0' in result
    
    def test_format_currency_negative(self):
        """Test format currency dengan nilai negatif"""
        result = format_currency(-50000)
        
        assert 'Rp' in result
        assert '-' in result or '(' in result  # Negative indicator
    
    def test_format_currency_decimal(self):
        """Test format currency dengan desimal"""
        result = format_currency(1000000.50)
        
        assert 'Rp' in result
        # Check if decimals are handled
        assert isinstance(result, str)
    
    def test_format_currency_large_number(self):
        """Test format currency dengan angka besar"""
        result = format_currency(1000000000)  # 1 billion
        
        assert 'Rp' in result
        assert '1.000.000.000' in result or '1,000,000,000' in result
    
    def test_format_currency_none(self):
        """Test format currency dengan None"""
        result = format_currency(None)
        
        assert result == '-' or result == 'Rp 0'


class TestFormatPhoneNumber:
    """Test format_phone_number function"""
    
    def test_format_phone_08_prefix(self):
        """Test format nomor dengan prefix 08"""
        result = format_phone_number('081234567890')
        
        # Format: "0812-3456-7890" or similar
        assert result.startswith('08')
        assert len(result) >= 12
    
    def test_format_phone_62_prefix(self):
        """Test format nomor dengan prefix 62"""
        result = format_phone_number('6281234567890')
        
        # Should convert to 08 format or keep 62
        assert '62' in result or result.startswith('08')
    
    def test_format_phone_with_spaces(self):
        """Test format nomor dengan spasi"""
        result = format_phone_number('0812 3456 7890')
        
        # Should remove spaces and format
        assert ' ' not in result or '-' in result
        assert '0812' in result or '812' in result
    
    def test_format_phone_with_dashes(self):
        """Test format nomor yang sudah ada dash"""
        result = format_phone_number('0812-3456-7890')
        
        # Should handle existing dashes
        assert '0812' in result or '812' in result
    
    def test_format_phone_none(self):
        """Test format dengan phone None"""
        result = format_phone_number(None)
        
        assert result == '-' or result == ''
    
    def test_format_phone_empty(self):
        """Test format dengan string kosong"""
        result = format_phone_number('')
        
        assert result == '-' or result == ''


class TestFormattingEdgeCases:
    """Test edge cases untuk formatting functions"""
    
    def test_timezone_conversion_consistency(self):
        """Test konsistensi konversi timezone"""
        utc_dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        
        # Format should be consistent
        result1 = format_datetime(utc_dt)
        result2 = format_datetime(utc_dt)
        
        assert result1 == result2
    
    def test_format_with_microseconds(self):
        """Test format dengan microseconds"""
        dt = datetime(2025, 1, 1, 12, 30, 45, 123456, tzinfo=pytz.UTC)
        result = format_datetime(dt)
        
        # Should handle microseconds gracefully
        assert isinstance(result, str)
        assert len(result) > 0
