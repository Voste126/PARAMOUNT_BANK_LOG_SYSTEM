from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from Staff.models import Staff
from ReportLog.models import ITIssue
from django.test import override_settings
import warnings

# Suppress all warnings to avoid unnecessary output during test execution
warnings.filterwarnings("ignore")
# Suppress specific DeprecationWarning for valid_group_name in channels_redis
warnings.filterwarnings("ignore", category=DeprecationWarning, message="valid_group_name is deprecated, use require_valid_group_name instead.")

@pytest.mark.django_db
def test_itissue_list_requires_auth():
    client = APIClient()
    response = client.get(reverse('issue-list-create'))
    assert response.status_code == 401 or response.status_code == 403

@pytest.mark.django_db
def test_itissue_create_authenticated():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        staff = Staff.objects.create_user(email='staff@paramount.co.ke', first_name='Staff', last_name='User', password='pass', is_verified=True)
        client = APIClient()
        client.force_authenticate(user=staff)
        data = {
            'issue_title': 'Printer not working',
            'category': 'hardware_issue',
            'priority': 'High',
            'issue_description': 'The main office printer is not working.',
            'method_of_logging': 'gmail',
        }
        # Use multipart to match the view's parser_classes
        response = client.post(reverse('issue-list-create'), data, format='multipart')
        # Print response for debugging if test fails
        if response.status_code == 400:
            print('Response data:', response.data)
        assert response.status_code in (201, 200)
        assert ITIssue.objects.filter(issue_title='Printer not working').exists()

@pytest.mark.django_db
def test_itissue_list_authenticated():
    with override_settings(STAFF_EMAIL_DOMAIN='@paramount.co.ke'):
        staff = Staff.objects.create_user(email='staff2@paramount.co.ke', first_name='Staff2', last_name='User2', password='pass', is_verified=True)
        ITIssue.objects.create(issue_title='Network down', category='network', priority='medium', issue_description='No internet.', method_of_logging='web', submitted_by=staff)
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.get(reverse('issue-list-create'))
        assert response.status_code == 200
        assert any(issue['issue_title'] == 'Network down' for issue in response.data)

@pytest.mark.django_db
def test_itissue_detail_requires_auth():
    client = APIClient()
    response = client.get(reverse('issue-detail', args=[1]))
    assert response.status_code == 401 or response.status_code == 403

# Add more tests for update, delete, and edge cases as needed
