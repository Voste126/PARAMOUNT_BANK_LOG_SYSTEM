import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from Staff.models import Staff
from django.test import override_settings
from django.utils import timezone

@pytest.mark.django_db
def test_staff_register_success():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@paramount.co.ke"
        }
        response = client.post(reverse('staff-register'), data)
        assert response.status_code == 201
        assert 'An OTP has been sent to your email.' in response.data['message']
        assert Staff.objects.filter(email="testuser@paramount.co.ke").exists()

@pytest.mark.django_db
def test_staff_register_invalid_email():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@gmail.com"
        }
        response = client.post(reverse('staff-register'), data)
        assert response.status_code == 400
        assert 'email' in response.data

@pytest.mark.django_db
def test_otp_login_request_unverified():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Unverified", last_name="User", email="unverified@paramount.co.ke", is_verified=False)
        data = {"email": staff.email}
        response = client.post(reverse('otp-login-request'), data)
        assert response.status_code == 403
        assert 'Email not verified.' in response.data['error']

@pytest.mark.django_db
def test_otp_login_request_verified():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Verified", last_name="User", email="verified@paramount.co.ke", is_verified=True)
        data = {"email": staff.email}
        response = client.post(reverse('otp-login-request'), data)
        assert response.status_code == 200
        assert 'OTP sent to email.' in response.data['message']

@pytest.mark.django_db
def test_staff_list_requires_auth():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        response = client.get(reverse('staff-list'))
        assert response.status_code in [401, 403]

@pytest.mark.django_db
def test_otp_login_verify_success():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Verified", last_name="User", email="verified@paramount.co.ke", is_verified=True, otp="123456", otp_created_at=timezone.now())
        data = {"email": staff.email, "otp": "123456"}
        response = client.post(reverse('otp-login-verify'), data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

@pytest.mark.django_db
def test_otp_login_verify_invalid_otp():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Verified", last_name="User", email="verified@paramount.co.ke", is_verified=True, otp="123456", otp_created_at=timezone.now())
        data = {"email": staff.email, "otp": "654321"}
        response = client.post(reverse('otp-login-verify'), data)
        assert response.status_code == 400
        assert 'Invalid OTP.' in response.data['error']