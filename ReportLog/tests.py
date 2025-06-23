import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
import uuid

from Staff.models import Staff
from ReportLog.models import ITIssue


@pytest.mark.django_db
class TestITIssueModel:
    """Test cases for ITIssue model functionality"""
    
    def test_it_issue_creation(self):
        """Test creating an IT issue with all required fields"""
        staff = Staff.objects.create(
            first_name="Test", 
            last_name="User", 
            email="test@paramount.co.ke", 
            is_verified=True
        )
        
        issue = ITIssue.objects.create(
            category='network_issue',
            issue_title='Network connectivity problem',
            issue_description='Unable to connect to internal servers',
            priority='High',
            method_of_logging='email',
            submitted_by=staff
        )
        
        assert issue.id is not None
        assert isinstance(issue.id, uuid.UUID)
        assert issue.category == 'network_issue'
        assert issue.issue_title == 'Network connectivity problem'
        assert issue.status == 'new'  # default status
        assert issue.submitted_by == staff
        assert issue.date_logged is not None
        assert issue.resolution_date is None

    def test_it_issue_str_representation(self):
        """Test string representation of ITIssue"""
        staff = Staff.objects.create(
            first_name="Test", 
            last_name="User", 
            email="test@paramount.co.ke"
        )
        
        issue = ITIssue.objects.create(
            issue_title='Test Issue Title',
            issue_description='Test description',
            priority='Normal',
            method_of_logging='email',
            submitted_by=staff
        )
        
        assert str(issue) == 'Test Issue Title'

    def test_auto_resolution_date_on_completion(self):
        """Test that resolution_date is automatically set when status changes to completed"""
        staff = Staff.objects.create(
            first_name="Test", 
            last_name="User", 
            email="test@paramount.co.ke"
        )
        
        issue = ITIssue.objects.create(
            issue_title='Test Issue',
            issue_description='Test description',
            priority='Normal',
            method_of_logging='email',
            submitted_by=staff
        )
        
        # Initially no resolution date
        assert issue.resolution_date is None
        
        # Mark as completed
        issue.status = 'completed'
        issue.save()
        
        # Should now have resolution date
        issue.refresh_from_db()
        assert issue.resolution_date is not None


@pytest.mark.django_db
class TestITIssueListCreateView:
    """Test cases for IT Issue list and creation endpoints"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.client = APIClient()
        self.staff = Staff.objects.create(
            first_name="Test",
            last_name="User", 
            email="test@paramount.co.ke",
            is_verified=True
        )
        
    def test_list_issues_requires_authentication(self):
        """Test that listing issues requires authentication"""
        response = self.client.get(reverse('issue-list-create'))
        assert response.status_code in [401, 403]

    def test_list_issues_authenticated_user(self):
        """Test listing issues for authenticated user"""
        self.client.force_authenticate(user=self.staff)
        
        # Create some issues for this user
        ITIssue.objects.create(
            issue_title='Issue 1',
            issue_description='Description 1',
            priority='High',
            method_of_logging='email',
            submitted_by=self.staff
        )
        ITIssue.objects.create(
            issue_title='Issue 2',
            issue_description='Description 2',
            priority='Normal',
            method_of_logging='call',
            submitted_by=self.staff
        )
        
        response = self.client.get(reverse('issue-list-create'))
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_list_issues_only_own_issues(self):
        """Test that users only see their own issues"""
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User",
            email="other@paramount.co.ke"
        )
        
        # Create issue for current user
        ITIssue.objects.create(
            issue_title='My Issue',
            issue_description='My Description',
            priority='High',
            method_of_logging='email',
            submitted_by=self.staff
        )
        
        # Create issue for other user
        ITIssue.objects.create(
            issue_title='Other Issue',
            issue_description='Other Description',
            priority='Normal',
            method_of_logging='email',
            submitted_by=other_staff
        )
        
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(reverse('issue-list-create'))
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['issue_title'] == 'My Issue'

    @patch('ReportLog.views.send_mail')
    @patch('ReportLog.views.async_to_sync')
    def test_create_issue_success(self, mock_async_to_sync, mock_send_mail):
        """Test successful issue creation with email notifications"""
        self.client.force_authenticate(user=self.staff)
        
        data = {
            'category': 'network_issue',
            'issue_title': 'New Network Issue',
            'issue_description': 'Detailed description of the network problem',
            'priority': 'High',
            'method_of_logging': 'email'
        }
        
        response = self.client.post(reverse('issue-list-create'), data)
        
        assert response.status_code == 201
        assert response.data['issue_title'] == 'New Network Issue'
        assert response.data['category'] == 'network_issue'
        assert response.data['status'] == 'new'
        assert response.data['submitted_by'] == self.staff.id
        
        # Check that emails are sent
        assert mock_send_mail.call_count == 2  # One to staff, one to IT support
        
        # Check WebSocket notification
        mock_async_to_sync.assert_called()

    def test_create_issue_with_file(self):
        """Test creating issue with file attachment"""
        self.client.force_authenticate(user=self.staff)
        
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file content",
            content_type="text/plain"
        )
        
        data = {
            'category': 'hardware_issue',
            'issue_title': 'Hardware Problem',
            'issue_description': 'Hardware is not working',
            'priority': 'Critical',
            'method_of_logging': 'email',
            'associated_file': test_file
        }
        
        response = self.client.post(reverse('issue-list-create'), data, format='multipart')
        
        assert response.status_code == 201
        assert response.data['associated_file'] is not None

    def test_create_issue_missing_required_fields(self):
        """Test creating issue with missing required fields"""
        self.client.force_authenticate(user=self.staff)
        
        data = {
            'issue_title': 'Incomplete Issue'
            # Missing required fields
        }
        
        response = self.client.post(reverse('issue-list-create'), data)
        assert response.status_code == 400

    def test_create_issue_unauthenticated(self):
        """Test creating issue without authentication"""
        data = {
            'category': 'network_issue',
            'issue_title': 'Unauthorized Issue',
            'issue_description': 'This should fail',
            'priority': 'High',
            'method_of_logging': 'email'
        }
        
        response = self.client.post(reverse('issue-list-create'), data)
        assert response.status_code in [401, 403]


@pytest.mark.django_db 
class TestITIssueRetrieveUpdateDestroyView:
    """Test cases for IT Issue detail, update, and delete endpoints"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.client = APIClient()
        self.staff = Staff.objects.create(
            first_name="Test",
            last_name="User",
            email="test@paramount.co.ke",
            is_verified=True
        )
        self.issue = ITIssue.objects.create(
            category='network_issue',
            issue_title='Test Issue',
            issue_description='Test description',
            priority='Normal',
            method_of_logging='email',
            submitted_by=self.staff
        )

    def test_retrieve_issue_success(self):
        """Test retrieving an issue successfully"""
        self.client.force_authenticate(user=self.staff)
        
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        assert response.status_code == 200
        assert response.data['id'] == str(self.issue.id)
        assert response.data['issue_title'] == 'Test Issue'

    def test_retrieve_issue_unauthenticated(self):
        """Test retrieving issue without authentication"""
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        assert response.status_code in [401, 403]

    def test_retrieve_issue_not_owner(self):
        """Test that users cannot retrieve issues they don't own"""
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User",
            email="other@paramount.co.ke"
        )
        
        self.client.force_authenticate(user=other_staff)
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        assert response.status_code == 404

    @patch('ReportLog.views.send_mail')
    def test_update_issue_status_to_completed(self, mock_send_mail):
        """Test updating issue status to completed triggers resolution emails"""
        self.client.force_authenticate(user=self.staff)
        
        data = {
            'status': 'completed',
            'work_done': 'Fixed the network connectivity issue',
            'recommendation': 'Monitor network stability'
        }
        
        response = self.client.put(
            reverse('issue-detail', kwargs={'pk': self.issue.id}), 
            data
        )
        
        assert response.status_code == 200
        assert response.data['status'] == 'completed'
        assert response.data['work_done'] == 'Fixed the network connectivity issue'
        assert response.data['resolution_date'] is not None
        
        # Check that resolution emails are sent
        assert mock_send_mail.call_count >= 1

    def test_update_issue_status_in_progress(self):
        """Test updating issue status to in-progress"""
        self.client.force_authenticate(user=self.staff)
        
        data = {
            'status': 'in-progress',
            'work_done': 'Currently investigating the issue'
        }
        
        response = self.client.put(
            reverse('issue-detail', kwargs={'pk': self.issue.id}), 
            data
        )
        
        assert response.status_code == 200
        assert response.data['status'] == 'in-progress'
        assert response.data['work_done'] == 'Currently investigating the issue'

    def test_delete_issue_success(self):
        """Test deleting an issue successfully"""
        self.client.force_authenticate(user=self.staff)
        
        response = self.client.delete(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        assert response.status_code == 204
        assert not ITIssue.objects.filter(id=self.issue.id).exists()

    def test_delete_issue_not_owner(self):
        """Test that users cannot delete issues they don't own"""
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User", 
            email="other@paramount.co.ke"
        )
        
        self.client.force_authenticate(user=other_staff)
        response = self.client.delete(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCategoryChoicesView:
    """Test cases for category choices endpoint"""
    
    def test_get_category_choices(self):
        """Test getting category choices without authentication"""
        client = APIClient()
        response = client.get(reverse('category-choices'))
        
        assert response.status_code == 200
        assert len(response.data) > 0
        
        # Check that all expected categories are present
        categories = [item['id'] for item in response.data]
        expected_categories = [
            'internet_banking', 'mobile_banking', 'br_net', 
            'network_issue', 'hardware_issue', 'others'
        ]
        
        for category in expected_categories:
            assert category in categories


@pytest.mark.django_db
class TestStaffUpdateIssueView:
    """Test cases for staff issue updates endpoint"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        self.client = APIClient()
        self.staff = Staff.objects.create(
            first_name="Test",
            last_name="User",
            email="test@paramount.co.ke",
            is_verified=True
        )
        self.issue = ITIssue.objects.create(
            category='network_issue',
            issue_title='Test Issue',
            issue_description='Test description',
            priority='Normal',
            method_of_logging='email',
            submitted_by=self.staff
        )

    def test_staff_update_own_issue(self):
        """Test staff updating their own issue"""
        self.client.force_authenticate(user=self.staff)
        
        data = {
            'issue_title': 'Updated Issue Title',
            'priority': 'High',
            'category': 'hardware_issue'
        }
        
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        assert response.status_code == 200
        assert 'Issue updated successfully' in response.data['detail']
        
        # Verify the issue was updated
        self.issue.refresh_from_db()
        assert self.issue.issue_title == 'Updated Issue Title'
        assert self.issue.priority == 'High'
        assert self.issue.category == 'hardware_issue'

    def test_staff_cannot_update_others_issue(self):
        """Test that staff cannot update issues submitted by others"""
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User",
            email="other@paramount.co.ke"
        )
        
        self.client.force_authenticate(user=other_staff)
        
        data = {
            'issue_title': 'Malicious Update'
        }
        
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        assert response.status_code == 404
        assert 'Issue not found or permission denied' in response.data['detail']

    def test_staff_update_issue_unauthenticated(self):
        """Test updating issue without authentication"""
        data = {
            'issue_title': 'Unauthorized Update'
        }
        
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        assert response.status_code in [401, 403]

    def test_staff_update_nonexistent_issue(self):
        """Test updating a non-existent issue"""
        self.client.force_authenticate(user=self.staff)
        
        fake_uuid = uuid.uuid4()
        data = {
            'issue_title': 'Update Non-existent Issue'
        }
        
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': fake_uuid}),
            data
        )
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestITIssueChoices:
    """Test cases for model choice fields"""
    
    def test_priority_choices(self):
        """Test that all priority choices are available"""
        expected_priorities = ['Critical', 'High', 'Normal', 'Low']
        model_priorities = [choice[0] for choice in ITIssue.PRIORITY_CHOICES]
        
        for priority in expected_priorities:
            assert priority in model_priorities

    def test_status_choices(self):
        """Test that all status choices are available"""
        expected_statuses = ['new', 'in-progress', 'duplicate', 'follow-up', 'completed', 'unresolved']
        model_statuses = [choice[0] for choice in ITIssue.STATUS_CHOICES]
        
        for status in expected_statuses:
            assert status in model_statuses

    def test_method_choices(self):
        """Test that all method choices are available"""
        expected_methods = ['email', 'call']
        model_methods = [choice[0] for choice in ITIssue.METHOD_CHOICES]
        
        for method in expected_methods:
            assert method in model_methods

    def test_category_choices(self):
        """Test that all category choices are available"""
        expected_categories = [
            'internet_banking', 'mobile_banking', 'br_net', 
            'network_issue', 'hardware_issue', 'others'
        ]
        model_categories = [choice[0] for choice in ITIssue.CATEGORY_CHOICES]
        
        for category in expected_categories:
            assert category in model_categories
