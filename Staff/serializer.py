from rest_framework import serializers
from django.conf import settings
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for the Staff model, used for general staff data representation.
    
    This serializer provides a read-only view of staff information, including their
    verification status. It's used for retrieving staff details and list views.
    
    Fields:
        id (UUID): The unique identifier for the staff member
        first_name (str): Staff member's first name
        last_name (str): Staff member's last name
        email (str): Staff member's email address
        is_verified (bool): Whether the staff member's email is verified (read-only)
        branch (str): The branch where the staff member works
        role (str): The staff member's role in the system
    """
    class Meta:
        model = Staff
        fields = ['id', 'first_name', 'last_name', 'email', 'is_verified', 'branch', 'role']
        read_only_fields = ['is_verified']

class StaffRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for staff registration process.
    
    This serializer handles the creation of new staff members with custom validation
    for email domain and role assignment. It enforces organization email policy and
    proper role initialization.
    
    Fields:
        first_name (str): Staff member's first name
        last_name (str): Staff member's last name
        email (str): Staff member's email (must end with organization domain)
        branch (str): The branch where the staff member works
        role (str): The staff member's role (defaults to 'User')
        
    Validation:
        - Ensures email domain matches organization's domain
        - Automatically sets is_staff=True for Admin roles
    """
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'email', 'branch', 'role']

    def validate_email(self, value):
        domain = getattr(settings, 'STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
        if not value.endswith(domain):
            raise serializers.ValidationError(f'Email must end with {domain}')
        return value

    def create(self, validated_data):
        # Ensure the role is set correctly during registration
        role = validated_data.get('role', 'User')
        validated_data['role'] = role  # Explicitly set the role
        if role == 'Admin':
            validated_data['is_staff'] = True
        return super().create(validated_data)

class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer for OTP verification during email verification process.
    
    Used to validate the OTP sent to staff members' email addresses during
    registration or email updates. Ensures the OTP format matches requirements.
    
    Fields:
        email (str): The email address to verify
        otp (str): The 6-digit OTP code sent to the email
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class OTPLoginSerializer(serializers.Serializer):
    """
    Serializer for OTP-based login authentication.
    
    Handles the validation of OTP codes during the login process. This implements
    a passwordless authentication system using email and OTP codes.
    
    Fields:
        email (str): The email address of the staff member trying to log in
        otp (str): The 6-digit OTP code sent to the email for authentication
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
