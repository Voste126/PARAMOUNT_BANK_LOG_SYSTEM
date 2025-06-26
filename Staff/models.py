"""
Staff Models for Paramount Bank IT Log System

This module defines the custom user model and manager for staff authentication
and user management in the Paramount Bank IT issue logging system.

Key Features:
- Custom user model extending Django's AbstractBaseUser
- UUID primary keys for enhanced security
- Email-based authentication (no username)
- OTP (One-Time Password) authentication system
- Role-based access control (User/Admin)
- Branch assignment for organizational structure
- Email domain validation for security
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid


class StaffManager(BaseUserManager):
    """
    Custom manager for Staff model
    
    This manager handles the creation of regular users and superusers
    with the custom Staff model. It ensures proper validation and
    field setting during user creation.
    """
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a regular Staff user with email and password
        
        Args:
            email (str): User's email address (must end with company domain)
            first_name (str): User's first name
            last_name (str): User's last name
            password (str, optional): User's password
            **extra_fields: Additional fields for the user model
            
        Returns:
            Staff: The created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        # Normalize email to lowercase and proper format
        email = self.normalize_email(email)
        
        # Create user instance with provided data
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        
        # Set password using Django's built-in password hashing
        user.set_password(password)
        
        # Save user to database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a superuser with admin privileges
        
        Args:
            email (str): Superuser's email address
            first_name (str): Superuser's first name
            last_name (str): Superuser's last name
            password (str, optional): Superuser's password
            **extra_fields: Additional fields for the user model
            
        Returns:
            Staff: The created superuser instance
        """
        # Set default superuser flags
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Create superuser using regular create_user method
        return self.create_user(email, first_name, last_name, password, **extra_fields)

class Staff(AbstractBaseUser, PermissionsMixin):
    """
    Custom Staff User Model for Paramount Bank
    
    This model represents staff members who can log and manage IT issues.
    It extends Django's AbstractBaseUser to provide custom authentication
    and user management functionality.
    
    Key Features:
    - UUID primary key for enhanced security
    - Email-based authentication (no username)
    - OTP authentication system for secure login
    - Role-based access control
    - Branch assignment for organizational structure
    - Email domain validation
    - Automatic admin privilege assignment based on role
    """
    
    # Primary key using UUID for better security and uniqueness
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the staff member"
    )
    
    # Basic personal information
    first_name = models.CharField(
        max_length=30,
        help_text="Staff member's first name"
    )
    last_name = models.CharField(
        max_length=30,
        help_text="Staff member's last name"
    )
    
    # Email field used for authentication (replaces username)
    email = models.EmailField(
        unique=True,
        help_text="Staff member's email address (must end with company domain)"
    )
    
    # Account verification and security fields
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the staff member's email has been verified"
    )
    
    # OTP (One-Time Password) fields for secure authentication
    otp = models.CharField(
        max_length=6, 
        blank=True, 
        null=True,
        help_text="Current OTP for authentication (6 digits)"
    )
    otp_created_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Timestamp when the OTP was generated"
    )
    
    # Standard Django user fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the staff member can log in"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Whether the staff member can access admin interface"
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text="When the staff member was created"
    )

    # Role-based access control choices
    ROLE_CHOICES = [
        ('User', 'User'),      # Regular staff member with basic permissions
        ('Admin', 'Admin'),    # Administrator with elevated permissions
    ]
    
    # Branch location choices for organizational structure
    BRANCH_CHOICES = [
        ('Westlands', 'Westlands branch'),
        ('Parklands', 'Parklands branch'),
        ('Koinange', 'Koinange branch'),
        ('Industrial', 'Industrial area branch'),
        ('Kisumu', 'Kisumu branch'),
        ('Mombasa', 'Mombasa branch'),
        ('Eldoret', 'Eldoret branch'),
        ('Headquarters', 'Headquarters'),
    ]

    # Role field determines user permissions and access level
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='User',
        help_text="Staff member's role determining their access level"
    )
    
    # Branch assignment for organizational tracking
    branch = models.CharField(
        max_length=20, 
        choices=BRANCH_CHOICES, 
        default='Headquarters',
        help_text="Branch where the staff member is located"
    )

    # Authentication configuration
    USERNAME_FIELD = 'email'  # Use email instead of username for login
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Required fields for superuser creation

    # Assign custom manager
    objects = StaffManager()

    def save(self, *args, **kwargs):
        """
        Custom save method with business logic validation
        
        This method enforces business rules before saving:
        1. Validates email domain matches company requirements
        2. Automatically sets admin privileges for Admin role users
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Raises:
            ValueError: If email domain doesn't match company requirements
        """
        # Get company email domain from settings (default: @paramount.co.ke)
        domain = getattr(settings, 'STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
        
        # Validate email domain for security
        if not self.email.endswith(domain):
            raise ValueError(f'Email must end with {domain}')
        
        # Automatically grant admin privileges to users with Admin role
        if self.role == 'Admin':
            self.is_staff = True
            
        # Call parent save method to complete the save operation
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the Staff model
        
        Returns:
            str: Full name of the staff member
        """
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        """
        Meta options for the Staff model
        """
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['first_name', 'last_name']

