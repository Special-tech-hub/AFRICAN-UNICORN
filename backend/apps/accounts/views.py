"""
Authentication views: Register, OTP verify/resend, Login, Logout.
"""
import logging
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .exceptions import (
    OTPCooldownError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    OTPNotFoundError,
)
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    OTPResendSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import OTPService

logger = logging.getLogger(__name__)


@extend_schema(tags=['Authentication'])
class RegisterView(APIView):
    """Register a new driver account and send OTP."""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        request=RegisterSerializer,
        responses={201: OpenApiResponse(description='Registration successful, OTP sent.')},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            OTPService.generate_and_send(user)
        except OTPCooldownError as e:
            pass  # Newly created user, cooldown shouldn't apply — log and continue
        except Exception as e:
            logger.error(f"Failed to send OTP during registration: {e}")

        return Response(
            {
                'message': 'Registration successful. An OTP has been sent to your phone number.',
                'phone_number': user.phone_number,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Authentication'])
class OTPVerifyView(APIView):
    """Verify OTP and activate driver account."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=OTPVerifySerializer,
        responses={200: OpenApiResponse(description='OTP verified, JWT tokens returned.')},
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        submitted_otp = serializer.validated_data['otp']

        try:
            user = OTPService.verify(phone_number, submitted_otp)
        except OTPNotFoundError as e:
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except OTPExpiredError as e:
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except OTPInvalidError as e:
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except OTPMaxAttemptsError as e:
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


@extend_schema(tags=['Authentication'])
class OTPResendView(APIView):
    """Resend OTP to the user's phone number (rate limited)."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=OTPResendSerializer,
        responses={200: OpenApiResponse(description='OTP resent successfully.')},
    )
    def post(self, request):
        from django_ratelimit.decorators import ratelimit
        from django_ratelimit.exceptions import Ratelimited

        serializer = OTPResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        try:
            from .models import User
            user = User.objects.get(phone_number=phone_number)
            OTPService.generate_and_send(user)
        except OTPCooldownError as e:
            return Response(
                {'error': True, 'message': str(e), 'retry_after': e.remaining_seconds},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except Exception as e:
            logger.error(f"OTP resend error for {phone_number}: {e}")
            return Response({'error': True, 'message': 'Failed to resend OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP resent successfully.'})


@extend_schema(tags=['Authentication'])
class LoginView(APIView):
    """Login with phone number and password."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiResponse(description='Login successful, JWT tokens returned.')},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        logger.info(f"User logged in: {user.phone_number} ({user.role})")

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    """Blacklist the refresh token to log out."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={204: OpenApiResponse(description='Logout successful.')},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return Response({'error': True, 'message': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
