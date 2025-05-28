from django.test import TestCase
from django.core.mail import send_mail
from django.conf import settings

class EmailTestCase(TestCase):
    def test_email_sending(self):
        # Test email details
        subject = "Test Email from PARAMOUNT"
        message = "This is a test email to verify SMTP configuration."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.IT_SUPPORT_EMAIL]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print("Test email sent successfully.")
        except Exception as e:
            self.fail(f"Error sending test email: {e}")
