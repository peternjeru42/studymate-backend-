import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


@pytest.mark.django_db
def test_register_and_login(api_client, user_payload):
    register_response = api_client.post("/api/v1/auth/register/", user_payload, format="json")
    assert register_response.status_code == 201
    register_data = register_response.json()["data"]
    assert register_data["user"]["email"] == user_payload["email"]
    assert "access" in register_data
    assert "refresh" in register_data

    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"email": user_payload["email"], "password": user_payload["password"]},
        format="json",
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["user"]["name"] == "Alex Thompson"


@pytest.mark.django_db
def test_profile_and_preferences_update(auth_client):
    profile_response = auth_client.patch(
        "/api/v1/auth/profile/",
        {
            "first_name": "Alex",
            "profile": {
                "current_semester": "Spring 2026",
                "onboarding_completed": True,
                "weekly_study_target_hours": 18,
            },
        },
        format="json",
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["data"]["profile"]["current_semester"] == "Spring 2026"

    preferences_response = auth_client.patch(
        "/api/v1/auth/preferences/",
        {
            "study_preferences": {
                "preferred_study_time": "morning",
                "session_duration": 60,
                "break_duration": 10,
                "study_style": "visual",
                "max_sessions_per_day": 4,
            }
        },
        format="json",
    )
    assert preferences_response.status_code == 200
    assert preferences_response.json()["data"]["study_preferences"]["session_duration"] == 60


@pytest.mark.django_db
def test_forgot_and_reset_password_flow(api_client, user_payload):
    api_client.post("/api/v1/auth/register/", user_payload, format="json")
    user = User.objects.get(email=user_payload["email"])

    forgot_response = api_client.post(
        "/api/v1/auth/forgot-password/",
        {"email": user_payload["email"]},
        format="json",
    )
    assert forgot_response.status_code == 200

    reset_response = api_client.post(
        "/api/v1/auth/reset-password/",
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": PasswordResetTokenGenerator().make_token(user),
            "new_password": "NewStrongPass123!",
        },
        format="json",
    )
    assert reset_response.status_code == 200

    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"email": user_payload["email"], "password": "NewStrongPass123!"},
        format="json",
    )
    assert login_response.status_code == 200
