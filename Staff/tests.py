import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from Staff.models import Staff
from django.test import override_settings
from django.utils import timezone

@pytest.mark.django_db
def test_staff_register_success():
    """
    Test successful staff registration with a valid email domain.
    - Ensures that a staff user can register with a valid @paramount.co.ke email.
    - Verifies that the response is 201 and an OTP message is sent.
    - Checks that the staff user is created in the database.
    """
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
    """
    Test staff registration with an invalid email domain.
    - Ensures registration fails if the email is not @paramount.co.ke.
    - Verifies that the response is 400 and the error is on the email field.
    """
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
    """
    Test OTP login request for an unverified staff user.
    - Ensures that OTP cannot be requested if the staff is not verified.
    - Verifies that the response is 403 and the error message is correct.
    """
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Unverified", last_name="User", email="unverified@paramount.co.ke", is_verified=False)
        data = {"email": staff.email}
        response = client.post(reverse('otp-login-request'), data)
        assert response.status_code == 403
        assert 'Email not verified.' in response.data['error']

@pytest.mark.django_db
def test_otp_login_request_verified():
    """
    Test OTP login request for a verified staff user.
    - Ensures that OTP can be requested if the staff is verified.
    - Verifies that the response is 200 and the OTP sent message is present.
    """
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Verified", last_name="User", email="verified@paramount.co.ke", is_verified=True)
        data = {"email": staff.email}
        response = client.post(reverse('otp-login-request'), data)
        assert response.status_code == 200
        assert 'OTP sent to email.' in response.data['message']

@pytest.mark.django_db
def test_staff_list_requires_auth():
    """
    Test that staff list endpoint requires authentication.
    - Ensures that unauthenticated users cannot access the staff list.
    - Verifies that the response is 401 or 403.
    """
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        response = client.get(reverse('staff-list'))
        assert response.status_code in [401, 403]

@pytest.mark.django_db
def test_otp_login_verify_success():
    """
    Test successful OTP login verification for a verified staff user.
    - Ensures that a valid OTP allows login and returns access/refresh tokens.
    - Verifies that the response is 200 and tokens are present in the response.
    """
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
    """
    Test OTP login verification with an invalid OTP.
    - Ensures that an incorrect OTP does not allow login.
    - Verifies that the response is 400 and the error message is correct.
    """
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        client = APIClient()
        staff = Staff.objects.create(first_name="Verified", last_name="User", email="verified@paramount.co.ke", is_verified=True, otp="123456", otp_created_at=timezone.now())
        data = {"email": staff.email, "otp": "654321"}
        response = client.post(reverse('otp-login-verify'), data)
        assert response.status_code == 400
        assert 'Invalid OTP.' in response.data['error']