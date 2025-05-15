from rest_framework import serializers
from django.conf import settings
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'first_name', 'last_name', 'email', 'is_verified']
        read_only_fields = ['is_verified']

class StaffRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        domain = getattr(settings, 'STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
        if not value.endswith(domain):
            raise serializers.ValidationError(f'Email must end with {domain}')
        return value

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class OTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
