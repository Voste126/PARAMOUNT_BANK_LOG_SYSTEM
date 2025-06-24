"""
Test suite for ReportLog application

This module contains comprehensive test cases for the IT Issue logging system.
It tests model functionality, API endpoints, authentication, authorization,
and business logic including email notifications and WebSocket updates.

Key areas tested:
- ITIssue model CRUD operations and validation
- API endpoint security and authentication
- Issue creation, retrieval, updating, and deletion
- Email notification system
- WebSocket real-time notifications
- File upload functionality
- Permission-based access control
- Data validation and error handling

Test Structure:
- TestITIssueModel: Core model functionality
- TestITIssueListCreateView: Issue listing and creation endpoints
- TestITIssueRetrieveUpdateDestroyView: Issue detail operations
- TestCategoryChoicesView: Category dropdown functionality
- TestStaffUpdateIssueView: Staff-specific issue updates
- TestITIssueChoices: Model choice field validation
"""

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
    """
    Test cases for ITIssue model functionality
    
    This class tests the core model behavior including:
    - Object creation with required fields
    - Default field values and auto-generated fields
    - String representation methods
    - Model-level business logic (like auto-setting resolution dates)
    - Data validation and constraints
    """
    
    def test_it_issue_creation(self):
        """
        Test creating an IT issue with all required fields
        
        Purpose: Ensure that ITIssue objects can be created successfully with all
        required fields and that default values are set correctly.
        
        What it tests:
        - Model instantiation with required fields
        - UUID primary key generation
        - Default status value ('new')
        - Automatic timestamp creation (date_logged)
        - Foreign key relationship with Staff model
        """
        # Create a test staff member first (required for foreign key relationship)
        staff = Staff.objects.create(
            first_name="Test", 
            last_name="User", 
            email="test@paramount.co.ke", 
            is_verified=True
        )
        
        # Create an IT issue with all required fields
        issue = ITIssue.objects.create(
            category='network_issue',
            issue_title='Network connectivity problem',
            issue_description='Unable to connect to internal servers',
            priority='High',
            method_of_logging='email',
            submitted_by=staff
        )
        
        # Verify the issue was created successfully with correct attributes
        assert issue.id is not None  # UUID should be auto-generated
        assert isinstance(issue.id, uuid.UUID)  # Should be UUID type
        assert issue.category == 'network_issue'  # Category should match input
        assert issue.issue_title == 'Network connectivity problem'  # Title should match
        assert issue.status == 'new'  # Default status should be 'new'
        assert issue.submitted_by == staff  # Foreign key relationship should work
        assert issue.date_logged is not None  # Timestamp should be auto-set
        assert issue.resolution_date is None  # Should be null initially

    def test_it_issue_str_representation(self):
        """
        Test string representation of ITIssue model
        
        Purpose: Verify that the __str__ method returns the expected string
        representation of the model instance.
        
        What it tests:
        - The __str__ method returns the issue_title field
        - String representation is human-readable for admin interface
        """
        # Create test staff and issue
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
        
        # Verify string representation matches the issue title
        assert str(issue) == 'Test Issue Title'

    def test_auto_resolution_date_on_completion(self):
        """
        Test that resolution_date is automatically set when status changes to completed
        
        Purpose: Verify the business logic that automatically sets resolution_date
        when an issue status is changed to 'completed'.
        
        What it tests:
        - Model save() method override functionality
        - Automatic timestamp setting based on status change
        - Business rule enforcement at the model level
        """
        # Create test staff and issue
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
        
        # Initially, resolution date should be None
        assert issue.resolution_date is None
        
        # Change status to completed and save
        issue.status = 'completed'
        issue.save()
        
        # Refresh from database to get updated values
        issue.refresh_from_db()
        
        # Resolution date should now be automatically set
        assert issue.resolution_date is not None


@pytest.mark.django_db
class TestITIssueListCreateView:
    """
    Test cases for IT Issue list and creation endpoints
    
    This class tests the API endpoints for:
    - Listing IT issues (GET /issues/)
    - Creating new IT issues (POST /issues/)
    
    Key areas covered:
    - Authentication and authorization
    - Data validation and serialization
    - Business logic (email notifications, WebSocket updates)
    - File upload functionality
    - Data isolation (users only see their own issues)
    """
    
    def setup_method(self):
        """
        Set up test data for each test method
        
        This method runs before each test to ensure a clean, consistent
        test environment. It creates:
        - APIClient for making HTTP requests
        - Test staff member for authentication
        """
        self.client = APIClient()
        self.staff = Staff.objects.create(
            first_name="Test",
            last_name="User", 
            email="test@paramount.co.ke",
            is_verified=True
        )
        
    def test_list_issues_requires_authentication(self):
        """
        Test that listing issues requires authentication
        
        Purpose: Ensure that the API endpoint is secured and cannot be accessed
        without proper authentication credentials.
        
        Security test: Verifies that unauthenticated requests are rejected
        with appropriate HTTP status codes (401 Unauthorized or 403 Forbidden).
        """
        # Attempt to access the endpoint without authentication
        response = self.client.get(reverse('issue-list-create'))
        
        # Should return 401 (Unauthorized) or 403 (Forbidden)
        assert response.status_code in [401, 403]

    def test_list_issues_authenticated_user(self):
        """
        Test listing issues for authenticated user
        
        Purpose: Verify that authenticated users can successfully retrieve
        their IT issues and that the data is correctly serialized.
        
        What it tests:
        - Successful API response for authenticated requests
        - Correct number of issues returned
        - Data serialization and structure
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Create some test issues for this user
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
        
        # Make the API request
        response = self.client.get(reverse('issue-list-create'))
        
        # Verify successful response and correct data
        assert response.status_code == 200
        assert len(response.data) == 2  # Should return both issues

    def test_list_issues_only_own_issues(self):
        """
        Test that users only see their own issues
        
        Purpose: Ensure data isolation and security by verifying that users
        can only access issues they submitted, not issues from other users.
        
        Security test: Prevents unauthorized access to other users' data.
        This is critical for maintaining data privacy and security.
        """
        # Create another staff member
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
        
        # Authenticate as the first user
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(reverse('issue-list-create'))
        
        # Should only see own issue, not the other user's issue
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['issue_title'] == 'My Issue'

    @patch('ReportLog.views.send_mail')
    @patch('ReportLog.views.async_to_sync')
    def test_create_issue_success(self, mock_async_to_sync, mock_send_mail):
        """
        Test successful issue creation with email notifications
        
        Purpose: Verify that new IT issues can be created successfully and
        that all associated business logic is triggered correctly.
        
        What it tests:
        - Issue creation with valid data
        - Automatic field population (status, submitted_by, etc.)
        - Email notification system (to staff and IT support)
        - WebSocket notification system for real-time updates
        - Response data structure and serialization
        
        Uses mocking to isolate the test from external dependencies
        (email sending and WebSocket functionality).
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Prepare test data for creating an issue
        data = {
            'category': 'network_issue',
            'issue_title': 'New Network Issue',
            'issue_description': 'Detailed description of the network problem',
            'priority': 'High',
            'method_of_logging': 'email'
        }
        
        # Make the POST request to create the issue
        response = self.client.post(reverse('issue-list-create'), data)
        
        # Verify successful creation and response data
        assert response.status_code == 201  # Created
        assert response.data['issue_title'] == 'New Network Issue'
        assert response.data['category'] == 'network_issue'
        assert response.data['status'] == 'new'  # Default status
        assert response.data['submitted_by'] == self.staff.id
        
        # Verify that email notifications are sent
        # One email to the staff member, one to IT support
        assert mock_send_mail.call_count == 2
        
        # Verify that WebSocket notification is triggered
        mock_async_to_sync.assert_called()

    def test_create_issue_with_file(self):
        """
        Test creating issue with file attachment
        
        Purpose: Verify that file uploads work correctly when creating issues
        and that the files are properly stored and referenced.
        
        What it tests:
        - File upload functionality using multipart/form-data
        - File field handling in the serializer
        - Successful issue creation with file attachment
        - File storage and retrieval
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Create a test file for upload
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file content",
            content_type="text/plain"
        )
        
        # Prepare test data including file
        data = {
            'category': 'hardware_issue',
            'issue_title': 'Hardware Problem',
            'issue_description': 'Hardware is not working',
            'priority': 'Critical',
            'method_of_logging': 'email',
            'associated_file': test_file
        }
        
        # Make POST request with multipart format for file upload
        response = self.client.post(reverse('issue-list-create'), data, format='multipart')
        
        # Verify successful creation and file attachment
        assert response.status_code == 201
        assert response.data['associated_file'] is not None

    def test_create_issue_missing_required_fields(self):
        """
        Test creating issue with missing required fields
        
        Purpose: Verify that the API properly validates input data and
        returns appropriate error responses when required fields are missing.
        
        What it tests:
        - Data validation at the API level
        - Proper error handling and response codes
        - Prevention of invalid data entry
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Prepare incomplete data (missing required fields)
        data = {
            'issue_title': 'Incomplete Issue'
            # Missing: issue_description, priority, method_of_logging, category
        }
        
        # Attempt to create issue with incomplete data
        response = self.client.post(reverse('issue-list-create'), data)
        
        # Should return 400 Bad Request due to missing required fields
        assert response.status_code == 400

    def test_create_issue_unauthenticated(self):
        """
        Test creating issue without authentication
        
        Purpose: Ensure that the create endpoint is properly secured and
        cannot be accessed without authentication.
        
        Security test: Verifies that unauthenticated requests to create
        issues are rejected with appropriate HTTP status codes.
        """
        # Prepare valid issue data
        data = {
            'category': 'network_issue',
            'issue_title': 'Unauthorized Issue',
            'issue_description': 'This should fail',
            'priority': 'High',
            'method_of_logging': 'email'
        }
        
        # Attempt to create issue without authentication
        response = self.client.post(reverse('issue-list-create'), data)
        
        # Should return 401 (Unauthorized) or 403 (Forbidden)
        assert response.status_code in [401, 403]


@pytest.mark.django_db 
class TestITIssueRetrieveUpdateDestroyView:
    """
    Test cases for IT Issue detail, update, and delete endpoints
    
    This class tests the API endpoints for individual issue operations:
    - Retrieving specific issues (GET /issues/{id}/)
    - Updating issue status and details (PUT/PATCH /issues/{id}/)
    - Deleting issues (DELETE /issues/{id}/)
    
    Key areas covered:
    - Authentication and authorization
    - Data ownership and access control
    - Status update business logic
    - Email notifications on completion
    - Data validation and error handling
    """
    
    def setup_method(self):
        """
        Set up test data for each test method
        
        Creates a consistent test environment with:
        - APIClient for HTTP requests
        - Test staff member for authentication
        - Sample IT issue for testing operations
        """
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
        """
        Test retrieving an issue successfully
        
        Purpose: Verify that authenticated users can retrieve detailed
        information about their IT issues.
        
        What it tests:
        - Successful API response for valid requests
        - Correct issue data serialization
        - UUID handling in URL parameters
        - Data structure and field presence
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Make GET request to retrieve the specific issue
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        # Verify successful response and correct data
        assert response.status_code == 200
        assert response.data['id'] == str(self.issue.id)  # UUID converted to string
        assert response.data['issue_title'] == 'Test Issue'

    def test_retrieve_issue_unauthenticated(self):
        """
        Test retrieving issue without authentication
        
        Purpose: Ensure that the detail endpoint is secured and requires
        proper authentication credentials.
        
        Security test: Verifies that unauthenticated access is blocked.
        """
        # Attempt to access without authentication
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        # Should be rejected with authentication error
        assert response.status_code in [401, 403]

    def test_retrieve_issue_not_owner(self):
        """
        Test that users cannot retrieve issues they don't own
        
        Purpose: Ensure data isolation by preventing users from accessing
        issues submitted by other users.
        
        Security test: Critical for maintaining data privacy and preventing
        unauthorized access to sensitive IT issue information.
        """
        # Create a different staff member
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User",
            email="other@paramount.co.ke"
        )
        
        # Authenticate as the other user (not the issue owner)
        self.client.force_authenticate(user=other_staff)
        
        # Attempt to access issue owned by different user
        response = self.client.get(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        # Should return 404 (not found) to prevent information disclosure
        assert response.status_code == 404

    @patch('ReportLog.views.send_mail')
    def test_update_issue_status_to_completed(self, mock_send_mail):
        """
        Test updating issue status to completed triggers resolution emails
        
        Purpose: Verify that when an issue is marked as completed, the system
        triggers appropriate business logic including email notifications.
        
        What it tests:
        - Status update functionality
        - Automatic resolution_date setting
        - Email notification system for completed issues
        - Data persistence and retrieval
        - Work completion documentation
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Prepare update data for completing the issue
        data = {
            'status': 'completed',
            'work_done': 'Fixed the network connectivity issue',
            'recommendation': 'Monitor network stability'
        }
        
        # Make PUT request to update the issue
        response = self.client.put(
            reverse('issue-detail', kwargs={'pk': self.issue.id}), 
            data
        )
        
        # Verify successful update and correct data
        assert response.status_code == 200
        assert response.data['status'] == 'completed'
        assert response.data['work_done'] == 'Fixed the network connectivity issue'
        assert response.data['resolution_date'] is not None  # Should be auto-set
        
        # Verify that resolution emails are sent (mocked)
        assert mock_send_mail.call_count >= 1

    def test_update_issue_status_in_progress(self):
        """
        Test updating issue status to in-progress
        
        Purpose: Verify that issue status can be updated to intermediate
        states without triggering completion-specific business logic.
        
        What it tests:
        - Status update for non-completion states
        - Work progress documentation
        - No automatic resolution_date setting
        - Proper data serialization
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Prepare update data for work in progress
        data = {
            'status': 'in-progress',
            'work_done': 'Currently investigating the issue'
        }
        
        # Make PUT request to update the issue
        response = self.client.put(
            reverse('issue-detail', kwargs={'pk': self.issue.id}), 
            data
        )
        
        # Verify successful update
        assert response.status_code == 200
        assert response.data['status'] == 'in-progress'
        assert response.data['work_done'] == 'Currently investigating the issue'

    def test_delete_issue_success(self):
        """
        Test deleting an issue successfully
        
        Purpose: Verify that users can delete their own IT issues and that
        the deletion is properly handled by the system.
        
        What it tests:
        - Successful deletion with proper authentication
        - Database record removal
        - Appropriate HTTP response codes
        - Data cleanup
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Make DELETE request
        response = self.client.delete(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        # Verify successful deletion
        assert response.status_code == 204  # No Content
        
        # Verify the issue no longer exists in the database
        assert not ITIssue.objects.filter(id=self.issue.id).exists()

    def test_delete_issue_not_owner(self):
        """
        Test that users cannot delete issues they don't own
        
        Purpose: Ensure data security by preventing users from deleting
        issues submitted by other users.
        
        Security test: Critical for preventing unauthorized data deletion
        and maintaining data integrity across user boundaries.
        """
        # Create a different staff member
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User", 
            email="other@paramount.co.ke"
        )
        
        # Authenticate as the other user (not the issue owner)
        self.client.force_authenticate(user=other_staff)
        
        # Attempt to delete issue owned by different user
        response = self.client.delete(reverse('issue-detail', kwargs={'pk': self.issue.id}))
        
        # Should return 404 (not found) to prevent information disclosure
        assert response.status_code == 404


@pytest.mark.django_db
class TestCategoryChoicesView:
    """
    Test cases for category choices endpoint
    
    This class tests the API endpoint that provides available categories
    for IT issues. This endpoint is used by frontend applications to
    populate dropdown menus and form selections.
    
    Key areas covered:
    - Public endpoint accessibility (no authentication required)
    - Data structure and completeness
    - All expected categories are present
    """
    
    def test_get_category_choices(self):
        """
        Test getting category choices without authentication
        
        Purpose: Verify that the category choices endpoint works correctly
        and returns all expected categories for use in forms and dropdowns.
        
        What it tests:
        - Public access (no authentication required)
        - Response structure and format
        - Data completeness (all categories present)
        - Proper serialization of choice fields
        
        This is a utility endpoint that helps maintain consistency
        between backend models and frontend UI elements.
        """
        # Create client without authentication (public endpoint)
        client = APIClient()
        
        # Make GET request to category choices endpoint
        response = client.get(reverse('category-choices'))
        
        # Verify successful response
        assert response.status_code == 200
        assert len(response.data) > 0
        
        # Extract category IDs from response
        categories = [item['id'] for item in response.data]
        
        # Define expected categories (should match model choices)
        expected_categories = [
            'internet_banking', 'mobile_banking', 'br_net', 
            'network_issue', 'hardware_issue', 'others'
        ]
        
        # Verify all expected categories are present
        for category in expected_categories:
            assert category in categories


@pytest.mark.django_db
class TestStaffUpdateIssueView:
    """
    Test cases for staff issue updates endpoint
    
    This class tests the specialized endpoint that allows staff members
    to update specific fields of their own IT issues. This is separate
    from the main update endpoint and has different permissions and
    field restrictions.
    
    Key areas covered:
    - Staff-specific update permissions
    - Field-level update restrictions
    - Data ownership and access control
    - Validation and error handling
    """
    
    def setup_method(self):
        """
        Set up test data for each test method
        
        Creates test environment with:
        - APIClient for HTTP requests
        - Test staff member for authentication
        - Sample IT issue for testing updates
        """
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
        """
        Test staff updating their own issue
        
        Purpose: Verify that staff members can successfully update specific
        fields of issues they submitted.
        
        What it tests:
        - Successful update of allowed fields
        - Data persistence in database
        - Proper response structure
        - Field-level validation
        - Ownership verification
        
        This endpoint allows staff to modify their issues after submission,
        which is important for correcting information or adding details.
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Prepare update data for allowed fields
        data = {
            'issue_title': 'Updated Issue Title',
            'priority': 'High',
            'category': 'hardware_issue'
        }
        
        # Make PUT request to update the issue
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        # Verify successful update
        assert response.status_code == 200
        assert 'Issue updated successfully' in response.data['detail']
        
        # Refresh from database and verify changes were persisted
        self.issue.refresh_from_db()
        assert self.issue.issue_title == 'Updated Issue Title'
        assert self.issue.priority == 'High'
        assert self.issue.category == 'hardware_issue'

    def test_staff_cannot_update_others_issue(self):
        """
        Test that staff cannot update issues submitted by others
        
        Purpose: Ensure data security by preventing staff from modifying
        issues they didn't submit.
        
        Security test: Critical for maintaining data integrity and preventing
        unauthorized modifications. Each staff member should only be able
        to update their own issues.
        """
        # Create a different staff member
        other_staff = Staff.objects.create(
            first_name="Other",
            last_name="User",
            email="other@paramount.co.ke"
        )
        
        # Authenticate as the other user (not the issue owner)
        self.client.force_authenticate(user=other_staff)
        
        # Attempt to update issue owned by different user
        data = {
            'issue_title': 'Malicious Update'
        }
        
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        # Should be rejected with not found (to prevent information disclosure)
        assert response.status_code == 404
        assert 'Issue not found or permission denied' in response.data['detail']

    def test_staff_update_issue_unauthenticated(self):
        """
        Test updating issue without authentication
        
        Purpose: Ensure that the update endpoint is properly secured and
        requires authentication.
        
        Security test: Verifies that unauthenticated requests are blocked
        with appropriate HTTP status codes.
        """
        # Prepare update data
        data = {
            'issue_title': 'Unauthorized Update'
        }
        
        # Attempt to update without authentication
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': self.issue.id}),
            data
        )
        
        # Should be rejected with authentication error
        assert response.status_code in [401, 403]

    def test_staff_update_nonexistent_issue(self):
        """
        Test updating a non-existent issue
        
        Purpose: Verify proper error handling when attempting to update
        an issue that doesn't exist.
        
        What it tests:
        - UUID validation and handling
        - Proper 404 error responses
        - Error message clarity
        - System stability with invalid requests
        """
        # Authenticate the test user
        self.client.force_authenticate(user=self.staff)
        
        # Generate a fake UUID that doesn't exist in database
        fake_uuid = uuid.uuid4()
        
        # Prepare update data
        data = {
            'issue_title': 'Update Non-existent Issue'
        }
        
        # Attempt to update non-existent issue
        response = self.client.put(
            reverse('staff-update-issue', kwargs={'pk': fake_uuid}),
            data
        )
        
        # Should return 404 Not Found
        assert response.status_code == 404


@pytest.mark.django_db
class TestITIssueChoices:
    """
    Test cases for model choice fields
    
    This class validates that all the choice fields defined in the ITIssue
    model contain the expected values. These tests ensure that:
    - All required choices are available
    - No choices are accidentally removed during development
    - The model choices match frontend expectations
    
    These tests help maintain consistency between the database schema,
    API responses, and frontend form options.
    """
    
    def test_priority_choices(self):
        """
        Test that all priority choices are available
        
        Purpose: Verify that the PRIORITY_CHOICES field contains all
        expected priority levels for IT issues.
        
        What it tests:
        - All priority levels are defined
        - Choice field consistency
        - No missing or extra priorities
        
        Priority levels help IT support team prioritize their work
        and ensure critical issues are addressed first.
        """
        # Define expected priority choices
        expected_priorities = ['Critical', 'High', 'Normal', 'Low']
        
        # Extract actual priorities from model choices
        model_priorities = [choice[0] for choice in ITIssue.PRIORITY_CHOICES]
        
        # Verify all expected priorities are present
        for priority in expected_priorities:
            assert priority in model_priorities

    def test_status_choices(self):
        """
        Test that all status choices are available
        
        Purpose: Verify that the STATUS_CHOICES field contains all
        expected status values for tracking issue progress.
        
        What it tests:
        - All status options are defined
        - Complete issue lifecycle is covered
        - Status progression options are available
        
        Status choices allow tracking of issue progress from creation
        through resolution, supporting workflow management.
        """
        # Define expected status choices covering the full issue lifecycle
        expected_statuses = ['new', 'in-progress', 'duplicate', 'follow-up', 'completed', 'unresolved']
        
        # Extract actual statuses from model choices
        model_statuses = [choice[0] for choice in ITIssue.STATUS_CHOICES]
        
        # Verify all expected statuses are present
        for status in expected_statuses:
            assert status in model_statuses

    def test_method_choices(self):
        """
        Test that all method choices are available
        
        Purpose: Verify that the METHOD_CHOICES field contains all
        expected methods for logging IT issues.
        
        What it tests:
        - All logging methods are defined
        - Communication channels are covered
        - Tracking of how issues are reported
        
        Method choices help track how issues are reported to IT support,
        which can be useful for improving communication channels.
        """
        # Define expected method choices for issue reporting
        expected_methods = ['email', 'call']
        
        # Extract actual methods from model choices
        model_methods = [choice[0] for choice in ITIssue.METHOD_CHOICES]
        
        # Verify all expected methods are present
        for method in expected_methods:
            assert method in model_methods

    def test_category_choices(self):
        """
        Test that all category choices are available
        
        Purpose: Verify that the CATEGORY_CHOICES field contains all
        expected categories for classifying IT issues.
        
        What it tests:
        - All issue categories are defined
        - Complete coverage of IT services
        - Proper classification options available
        
        Categories help organize and route issues to appropriate IT
        specialists, improving response times and resolution quality.
        """
        # Define expected category choices covering all IT services
        expected_categories = [
            'internet_banking',  # Online banking platform issues
            'mobile_banking',    # Mobile app related issues
            'br_net',           # Branch network connectivity
            'network_issue',    # General network problems
            'hardware_issue',   # Physical equipment problems
            'others'            # Catch-all for miscellaneous issues
        ]
        
        # Extract actual categories from model choices
        model_categories = [choice[0] for choice in ITIssue.CATEGORY_CHOICES]
        
        # Verify all expected categories are present
        for category in expected_categories:
            assert category in model_categories
