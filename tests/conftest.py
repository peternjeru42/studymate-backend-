import os

import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def configure_test_env(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.OPENAI_API_KEY = ""
    yield


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_payload():
    return {
        "email": "alex@example.com",
        "name": "Alex Thompson",
        "password": "StrongPass123!",
    }


@pytest.fixture
def registered_user(db, api_client, user_payload):
    response = api_client.post("/api/v1/auth/register/", user_payload, format="json")
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def auth_client(db, api_client, registered_user, user_payload):
    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"email": user_payload["email"], "password": user_payload["password"]},
        format="json",
    )
    token = login_response.json()["data"]["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
