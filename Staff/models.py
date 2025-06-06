from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid

class StaffManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)

class Staff(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    ROLE_CHOICES = [
        ('User', 'User'),
        ('Admin', 'Admin'),
    ]
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

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, default='Headquarters')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = StaffManager()

    def save(self, *args, **kwargs):
        domain = getattr(settings, 'STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
        if not self.email.endswith(domain):
            raise ValueError(f'Email must end with {domain}')
        # Set is_staff to True if role is Admin
        if self.role == 'Admin':
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

