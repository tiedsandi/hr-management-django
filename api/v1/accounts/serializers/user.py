from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    role = serializers.CharField(source='get_role_display', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'employee_id', 'email',
            'first_name', 'last_name', 'phone',
            'division', 'division_name', 'role',
            'is_active', 'date_joined', 'type_of_employment', 'status'
        ]
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer untuk register user baru"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'employee_id', 'email',
            'first_name', 'last_name', 'phone',
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password tidak cocok"
            })
        return attrs
    
    def validate_employee_id(self, value):
        """Validate employee_id unique"""
        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID sudah digunakan")
        return value
    
    def create(self, validated_data):
        """Create user dengan hashed password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer untuk login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Username atau password salah',
                    code='authentication'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Akun tidak aktif',
                    code='inactive'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Username dan password wajib diisi',
                code='required'
            )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer untuk change password"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password baru tidak cocok"
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password lama salah")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer untuk user profile (detail)"""
    role = serializers.CharField(source='get_role_display', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    has_complete_face_data = serializers.BooleanField(read_only=True)
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'employee_id', 'email',
            'first_name', 'last_name', 'phone',
            'division', 'division_name', 'hire_date',
            'role', 'groups',
            'face_photo_front', 'face_photo_left', 'face_photo_right',
            'has_complete_face_data',
            'is_active', 'date_joined', 'last_login', 'type_of_employment', 'status'
        ]
        read_only_fields = [
            'id', 'username', 'employee_id', 'date_joined', 
            'last_login', 'face_encoding'
        ]