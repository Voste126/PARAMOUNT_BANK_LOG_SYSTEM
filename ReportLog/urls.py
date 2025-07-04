from django.urls import path
from .views import ITIssueListCreateView, ITIssueRetrieveUpdateDestroyView, CategoryChoicesView, StaffUpdateIssueView

"""
URL Configuration for the ReportLog app

This module defines the URL patterns for handling IT issues and related functionality.
Each endpoint is documented with its purpose and available HTTP methods.
"""

urlpatterns = [
    # Endpoint for listing all issues and creating new ones
    # GET: Returns a list of all IT issues
    # POST: Creates a new IT issue
    path('issues/', ITIssueListCreateView.as_view(), name='issue-list-create'),

    # Endpoint for retrieving, updating, and deleting specific issues
    # GET: Returns details of a specific issue
    # PUT/PATCH: Updates an existing issue
    # DELETE: Removes an issue
    path('issues/<uuid:pk>/', ITIssueRetrieveUpdateDestroyView.as_view(), name='issue-detail'),

    # Endpoint for retrieving available category choices
    # GET: Returns a list of all available issue categories
    path('categories/', CategoryChoicesView.as_view(), name='category-choices'),

    # Endpoint for staff members to update issue status and details
    # PUT/PATCH: Updates an issue's status and details (staff only)
    path('issues/<uuid:pk>/update/', StaffUpdateIssueView.as_view(), name='staff-update-issue'),
]
