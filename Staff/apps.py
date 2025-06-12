from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Staff'

    def ready(self):
        User = get_user_model()
        try:
            if not User.objects.filter(email='admin@paramount.co.ke').exists():
                User.objects.create_superuser(
                    email='admin@paramount.co.ke',
                    password='Admin@123',
                    otp='123456',
                    is_verified=True
                )
        except IntegrityError:
            pass
