"""
Tests untuk core validators.
"""
import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import validate_image_file, validate_phone_number


class TestValidateImageFile:
    """Test validate_image_file function"""
    
    def test_valid_jpg_file(self):
        """Test validasi file JPG yang valid"""
        # Create a small valid file (< 5MB)
        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        # Should not raise exception
        try:
            validate_image_file(file)
        except ValidationError:
            pytest.fail("Valid JPG file should not raise ValidationError")
    
    def test_valid_png_file(self):
        """Test validasi file PNG yang valid"""
        file = SimpleUploadedFile(
            "test.png",
            b"fake image content",
            content_type="image/png"
        )
        
        try:
            validate_image_file(file)
        except ValidationError:
            pytest.fail("Valid PNG file should not raise ValidationError")
    
    def test_valid_jpeg_file(self):
        """Test validasi file JPEG yang valid"""
        file = SimpleUploadedFile(
            "test.jpeg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        try:
            validate_image_file(file)
        except ValidationError:
            pytest.fail("Valid JPEG file should not raise ValidationError")
    
    def test_invalid_file_extension(self):
        """Test validasi file dengan extension tidak valid"""
        file = SimpleUploadedFile(
            "test.gif",
            b"fake image content",
            content_type="image/gif"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            validate_image_file(file)
        
        assert 'JPG, JPEG, PNG' in str(exc_info.value)
    
    def test_file_too_large(self):
        """Test validasi file yang terlalu besar (> 5MB)"""
        # Create file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        file = SimpleUploadedFile(
            "test.jpg",
            large_content,
            content_type="image/jpeg"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            validate_image_file(file)
        
        assert '5MB' in str(exc_info.value) or 'size' in str(exc_info.value).lower()
    
    def test_file_exactly_5mb(self):
        """Test validasi file yang tepat 5MB (boundary)"""
        # Create file exactly 5MB
        content = b"x" * (5 * 1024 * 1024)
        file = SimpleUploadedFile(
            "test.jpg",
            content,
            content_type="image/jpeg"
        )
        
        # Should not raise exception (exactly at limit)
        try:
            validate_image_file(file)
        except ValidationError:
            pytest.fail("File exactly 5MB should be valid")
    
    def test_uppercase_extension(self):
        """Test validasi dengan extension uppercase"""
        file = SimpleUploadedFile(
            "test.JPG",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        try:
            validate_image_file(file)
        except ValidationError:
            pytest.fail("Uppercase extension should be valid")


class TestValidatePhoneNumber:
    """Test validate_phone_number function"""
    
    def test_valid_phone_08_prefix(self):
        """Test validasi nomor dengan prefix 08"""
        try:
            validate_phone_number('081234567890')
        except ValidationError:
            pytest.fail("Valid phone with 08 prefix should not raise error")
    
    def test_valid_phone_62_prefix(self):
        """Test validasi nomor dengan prefix 62"""
        try:
            validate_phone_number('6281234567890')
        except ValidationError:
            pytest.fail("Valid phone with 62 prefix should not raise error")
    
    def test_invalid_prefix(self):
        """Test validasi nomor dengan prefix tidak valid"""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone_number('0712345678')
        
        assert 'diawali 08 atau 62' in str(exc_info.value)
    
    def test_phone_too_short(self):
        """Test validasi nomor yang terlalu pendek"""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone_number('08123')
        
        assert '10-15 digit' in str(exc_info.value)
    
    def test_phone_too_long(self):
        """Test validasi nomor yang terlalu panjang"""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone_number('0812345678901234567890')
        
        assert '10-15 digit' in str(exc_info.value)
    
    def test_phone_min_length(self):
        """Test validasi nomor dengan panjang minimum (10 digit)"""
        try:
            validate_phone_number('0812345678')  # Exactly 10 digits
        except ValidationError:
            pytest.fail("Phone with 10 digits should be valid")
    
    def test_phone_max_length(self):
        """Test validasi nomor dengan panjang maksimum (15 digit)"""
        try:
            validate_phone_number('081234567890123')  # Exactly 15 digits
        except ValidationError:
            pytest.fail("Phone with 15 digits should be valid")
    
    def test_phone_with_spaces(self):
        """Test validasi nomor dengan spasi (should be cleaned)"""
        try:
            validate_phone_number('0812 3456 7890')
        except ValidationError:
            pytest.fail("Phone with spaces should be valid after cleaning")
    
    def test_phone_with_dashes(self):
        """Test validasi nomor dengan dash (should be cleaned)"""
        try:
            validate_phone_number('0812-3456-7890')
        except ValidationError:
            pytest.fail("Phone with dashes should be valid after cleaning")
    
    def test_phone_with_parentheses(self):
        """Test validasi nomor dengan kurung (should be cleaned)"""
        try:
            validate_phone_number('(0812) 3456-7890')
        except ValidationError:
            pytest.fail("Phone with parentheses should be valid after cleaning")
    
    def test_phone_with_plus_sign(self):
        """Test validasi nomor dengan tanda plus"""
        try:
            validate_phone_number('+6281234567890')
        except ValidationError:
            pytest.fail("Phone with + sign should be valid after cleaning")
    
    def test_empty_phone(self):
        """Test validasi dengan nomor kosong"""
        try:
            validate_phone_number('')
        except ValidationError:
            pytest.fail("Empty phone should not raise error (nullable)")
    
    def test_none_phone(self):
        """Test validasi dengan None"""
        try:
            validate_phone_number(None)
        except ValidationError:
            pytest.fail("None phone should not raise error (nullable)")
    
    def test_phone_with_letters(self):
        """Test validasi nomor dengan huruf"""
        with pytest.raises(ValidationError):
            validate_phone_number('08123ABC890')


class TestValidatorsEdgeCases:
    """Test edge cases untuk validators"""
    
    def test_image_with_no_extension(self):
        """Test image tanpa extension"""
        file = SimpleUploadedFile(
            "test",
            b"fake content",
            content_type="image/jpeg"
        )
        
        with pytest.raises(ValidationError):
            validate_image_file(file)
    
    def test_phone_only_prefix(self):
        """Test phone yang hanya prefix"""
        with pytest.raises(ValidationError):
            validate_phone_number('08')
    
    def test_phone_international_format(self):
        """Test phone format internasional lengkap"""
        try:
            validate_phone_number('+62 812 3456 7890')
        except ValidationError:
            pytest.fail("International format should be valid")
