from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    StudyPreferencesUpdateSerializer,
    UserSerializer,
)
from apps.common.responses import api_response

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return api_response(
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Account created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, message="Login successful.")


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(data=response.data, message="Token refreshed.")


class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return api_response(data=None, message="Logged out successfully.")


class ProfileAPIView(APIView):
    def get(self, request):
        return api_response(data=UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=UserSerializer(request.user).data, message="Profile updated successfully.")


class PreferencesAPIView(APIView):
    def get(self, request):
        return api_response(data=UserSerializer(request.user).data)

    def patch(self, request):
        serializer = StudyPreferencesUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(data=UserSerializer(request.user).data, message="Preferences updated successfully.")


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"/reset-password?uid={uid}&token={token}"
            send_mail(
                subject="StudyMate password reset",
                message=f"Use this link to reset your password: {reset_link}",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
        return api_response(data=None, message="If the account exists, a password reset email has been sent.")


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return api_response(data=None, message="Password reset successfully.")


class ChangePasswordAPIView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return api_response(data=None, message="Password changed successfully.")


class DeleteAccountAPIView(APIView):
    def delete(self, request):
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        return api_response(data=None, message="Account deactivated successfully.")


class ExportAccountDataAPIView(APIView):
    def get(self, request):
        payload = {
            "user": UserSerializer(request.user).data,
            "export_ready": False,
            "message": "Structured export is not implemented yet. Use this payload as a placeholder.",
        }
        return api_response(data=payload, message="Account export payload generated.")
