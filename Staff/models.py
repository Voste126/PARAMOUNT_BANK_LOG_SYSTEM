from django.db import models
from django.conf import settings

class Staff(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        domain = getattr(settings, 'STAFF_EMAIL_DOMAIN', '@paramount.co.ke')
        if not self.email.endswith(domain):
            raise ValueError(f'Email must end with {domain}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

