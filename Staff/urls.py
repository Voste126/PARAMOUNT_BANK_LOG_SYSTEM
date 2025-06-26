"""
URL Configuration for Staff Authentication and Management

This module defines all URL patterns for staff-related operations in the
Paramount Bank IT Log System. It includes endpoints for:

- User registration and email verification
- OTP-based authentication system
- User credential management
- Administrative user management functions

Security Features:
- OTP-based login for enhanced security
- Admin-only endpoints for user management
- UUID-based user identification
- Proper authentication required for sensitive operations
"""

from django.urls import path
from . import views
from .views import (
    ResendOTPView, 
    GetUserCredentialsView, 
    AdminUpdateUserCredentialsView, 
    AdminGetUserCredentialsView, 
    AdminCreateUserView
)

urlpatterns = [
    # === USER REGISTRATION & VERIFICATION ENDPOINTS ===
    
    path('register/', 
         views.StaffRegisterView.as_view(), 
         name='staff-register'),
    # POST: Register new staff member with email verification
    # Sends OTP to email for account verification
    
    path('verify-otp/', 
         views.OTPVerifyView.as_view(), 
         name='verify-otp'),
    # POST: Verify OTP sent during registration
    # Activates the user account after successful verification
    
    # === AUTHENTICATION ENDPOINTS ===
    
    path('login/request/', 
         views.OTPLoginRequestView.as_view(), 
         name='otp-login-request'),
    # POST: Request OTP for login (secure passwordless authentication)
    # Sends temporary OTP to user's verified email address
    
    path('login/verify/', 
         views.OTPLoginVerifyView.as_view(), 
         name='otp-login-verify'),
    # POST: Verify OTP and complete login process
    # Returns JWT access and refresh tokens on success
    
    path('logout/', 
         views.LogoutView.as_view(), 
         name='logout'),
    # POST: Logout user and invalidate tokens
    # Blacklists the refresh token for security
    
    # === USER MANAGEMENT ENDPOINTS ===
    
    path('all/', 
         views.StaffListView.as_view(), 
         name='staff-list'),
    # GET: List all staff members (admin only)
    # Returns paginated list of staff with basic information
    
    path('update-credentials/', 
         views.UpdateUserCredentialsView.as_view(), 
         name='update-credentials'),
    # PUT/PATCH: Update own user credentials and profile information
    # Allows users to modify their personal information
    
    path('resend-otp/', 
         ResendOTPView.as_view(), 
         name='resend-otp'),
    # POST: Resend OTP for verification or login
    # Handles both registration and login OTP resending
    
    path('get-user-credentials/<str:user_id>/', 
         GetUserCredentialsView.as_view(), 
         name='get-user-credentials'),
    # GET: Retrieve user's own credentials and profile
    # Users can only access their own information
    
    # === ADMINISTRATIVE ENDPOINTS ===
    # These endpoints require admin privileges and are used for user management
    
    path('admin/create-user/', 
         AdminCreateUserView.as_view(), 
         name='admin-create-user'),
    # POST: Create new staff member (admin only)
    # Allows admins to create user accounts without email verification
    
    path('admin/update-user/', 
         AdminUpdateUserCredentialsView.as_view(), 
         name='admin-update-user'),
    # PUT/PATCH: Update any user's credentials (admin only)
    # Allows admins to modify user information and roles
    
    path('admin/get-user-credentials/<uuid:user_id>/', 
         AdminGetUserCredentialsView.as_view(), 
         name='admin-get-user-credentials'),
    # GET: Retrieve any user's credentials (admin only)
    # Allows admins to view detailed user information
    
    path('admin/delete-user/<uuid:user_id>/', 
         views.AdminDeleteUserView.as_view(), 
         name='admin-delete-user'),
    # DELETE: Permanently delete a user account (admin only)
    # Removes user and all associated data from the system
]
