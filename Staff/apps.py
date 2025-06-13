from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate


def create_default_admin(sender, **kwargs):
    User = get_user_model()
    try:
        if not User.objects.filter(email='admin@paramount.co.ke').exists():
            User.objects.create_superuser(
                email='admin@paramount.co.ke',
                password='Admin@123',
                otp='123456',
                is_verified=True
            )
            print("Default admin user created successfully.")
    except Exception as e:
        print(f"Error creating default admin: {e}")


class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Staff'

    def ready(self):
        # Connect post_migrate signal to create default admin
        post_migrate.connect(create_default_admin, sender=self)
