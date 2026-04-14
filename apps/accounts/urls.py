from django.urls import path

from apps.accounts.views import (
    ChangePasswordAPIView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    DeleteAccountAPIView,
    ExportAccountDataAPIView,
    ForgotPasswordAPIView,
    LogoutAPIView,
    PreferencesAPIView,
    ProfileAPIView,
    RegisterAPIView,
    ResetPasswordAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("delete-account/", DeleteAccountAPIView.as_view(), name="delete-account"),
    path("export/", ExportAccountDataAPIView.as_view(), name="export-account"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("preferences/", PreferencesAPIView.as_view(), name="preferences"),
]
