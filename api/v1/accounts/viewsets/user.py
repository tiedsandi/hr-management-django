from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.v1.accounts.serializers.user import (
    ChangePasswordSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


@extend_schema(
    tags=['Authentication'],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description='User registered successfully'),
        400: OpenApiResponse(description='Validation error'),
    },
    summary='Register new user',
    description='Create a new user account with email and password'
)
class RegisterView(generics.CreateAPIView):
    """
    Register user baru.
    
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registrasi berhasil'
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description='Login successful'),
        400: OpenApiResponse(description='Invalid credentials'),
    },
    summary='Login user',
    description='Authenticate user and return JWT tokens'
)
class LoginView(APIView):
    """
    Login user.
    
    POST /api/v1/auth/login/
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login berhasil'
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    request={'refresh': 'string'},
    responses={
        200: OpenApiResponse(description='Logout successful'),
        400: OpenApiResponse(description='Invalid token'),
    },
    summary='Logout user',
    description='Blacklist refresh token to invalidate JWT session'
)
class LogoutView(APIView):
    """
    Logout user (blacklist refresh token).
    
    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout berhasil'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=['Users V1'],
    responses={
        200: ProfileSerializer,
    },
    summary='Get or update user profile',
    description='Retrieve or update authenticated user profile information'
)
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get & Update user profile.
    
    GET /api/v1/auth/profile/
    PUT /api/v1/auth/profile/
    PATCH /api/v1/auth/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['Users V1'],
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description='Password changed successfully'),
        400: OpenApiResponse(description='Invalid old password or validation error'),
    },
    summary='Change password',
    description='Change password for authenticated user'
)
class ChangePasswordView(APIView):
    """
    Change password.
    
    POST /api/v1/auth/change-password/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password berhasil diubah'
        }, status=status.HTTP_200_OK)