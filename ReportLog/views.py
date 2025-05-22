from rest_framework import generics, permissions
from .models import ITIssue
from .serializer import ITIssueSerializer, ITIssueCreateSerializer, ITIssueUpdateStatusSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.response import Response

class ITIssueListCreateView(generics.ListCreateAPIView):
    serializer_class = ITIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Short-circuit for schema generation (Swagger/OpenAPI)
        if getattr(self, 'swagger_fake_view', False):
            return ITIssue.objects.none()
        user = self.request.user
        from Staff.models import Staff
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="User not found", code="user_not_found")
        return ITIssue.objects.filter(submitted_by=staff)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ITIssueCreateSerializer
        return ITIssueSerializer

    def perform_create(self, serializer):
        from Staff.models import Staff
        user = self.request.user
        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="User not found", code="user_not_found")
        # Save the new IT issue and associate it with the staff member
        instance = serializer.save(submitted_by=staff)

        # --- EMAIL NOTIFICATION TO STAFF (REAL-TIME ON ISSUE LOGGED) ---
        # Send an email to the staff member confirming the issue was logged
        staff_email = staff.email
        if staff_email:
            subject = f"IT Issue Successfully Logged: {instance.issue_title}"
            message = (
                f"Dear {staff.first_name} {staff.last_name},\n\n"
                f"Your IT issue has been successfully logged in our system. Our IT team has been notified and will begin working on your request immediately. Please find the details of your logged issue below:\n\n"
                f"Issue Title: {instance.issue_title}\n"
                f"Category: {instance.category.replace('_', ' ').title()}\n"
                f"Priority: {instance.priority}\n"
                f"Date Logged: {instance.date_logged.strftime('%Y-%m-%d %H:%M:%S') if instance.date_logged else 'N/A'}\n\n"
                f"Issue Description:\n{instance.issue_description}\n\n"
                f"Method of Logging: {instance.method_of_logging.title()}\n\n"
                f"Our IT support team will review your issue and keep you updated on the progress. If you have any further information to add, please reply to this email or contact the IT department directly.\n\n"
                f"Thank you for bringing this to our attention.\n\n"
                f"Best regards,\nIT Support Team\nParamount Bank"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [staff_email],
                fail_silently=True,
            )

        # --- EMAIL NOTIFICATION TO IT SUPPORT (REAL-TIME ON ISSUE LOGGED) ---
        # Send an email to IT support with full details and staff name
        it_support_email = getattr(settings, 'IT_SUPPORT_EMAIL', None)
        if it_support_email:
            it_subject = f"New IT Issue Logged by {staff.first_name} {staff.last_name}: {instance.issue_title}"
            it_message = (
                f"A new IT issue has been logged by {staff.first_name} {staff.last_name} ({staff.email}).\n\n"
                f"Issue Details:\n"
                f"Title: {instance.issue_title}\n"
                f"Category: {instance.category.replace('_', ' ').title()}\n"
                f"Priority: {instance.priority}\n"
                f"Date Logged: {instance.date_logged.strftime('%Y-%m-%d %H:%M:%S') if instance.date_logged else 'N/A'}\n"
                f"Method of Logging: {instance.method_of_logging.title()}\n\n"
                f"Description:\n{instance.issue_description}\n\n"
                f"Please review and assign this issue as soon as possible.\n\n"
                f"--\nParamount Bank IT Issue Reporting System"
            )
            send_mail(
                it_subject,
                it_message,
                settings.DEFAULT_FROM_EMAIL,
                [it_support_email],
                fail_silently=True,
            )

        # --- REAL-TIME WEBSOCKET NOTIFICATION (ON ISSUE LOGGED) ---
        # Notify all dashboard clients via WebSocket about the new issue
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "notify",
                "message": {
                    "event": "new_issue",
                    "title": instance.issue_title,
                    "submitted_by": f"{staff.first_name} {staff.last_name}",
                    "priority": instance.priority,
                    "category": instance.category,
                    "date_logged": instance.date_logged.strftime('%Y-%m-%d %H:%M:%S') if instance.date_logged else 'N/A',
                }
            }
        )

        # Include the ID of the newly created issue in the response
        self.response = Response({
            "id": instance.id,
            "message": "Issue successfully created."
        }, status=201)

class ITIssueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ITIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Short-circuit for schema generation (Swagger/OpenAPI)
        if getattr(self, 'swagger_fake_view', False):
            return ITIssue.objects.none()
        user = self.request.user
        from Staff.models import Staff
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="User not found", code="user_not_found")
        return ITIssue.objects.filter(submitted_by=staff)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ITIssueUpdateStatusSerializer
        return ITIssueSerializer

    def perform_update(self, serializer):
        from Staff.models import Staff
        user = self.request.user
        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="User not found", code="user_not_found")
        # Only set submitted_by now
        instance = serializer.save(submitted_by=staff)
        from .serializer import ITIssueSerializer
        data = ITIssueSerializer(instance).data
        if instance.submitted_by:
            data['submitted_by'] = staff.id
        self.full_details = data

        # --- EMAIL NOTIFICATION TO STAFF AND IT SUPPORT (ON ISSUE RESOLVED) ---
        if hasattr(instance, 'status') and instance.status == 'completed':
            staff_email = instance.submitted_by.email if instance.submitted_by else None
            it_support_email = getattr(settings, 'IT_SUPPORT_EMAIL', None)
            if staff_email:
                subject = f"IT Issue Resolution Notification: {instance.issue_title}"
                message = (
                    f"Dear {instance.submitted_by.first_name} {instance.submitted_by.last_name},\n\n"
                    f"We are pleased to inform you that the IT issue you reported has been successfully resolved. Please find the details below:\n\n"
                    f"Issue Title: {instance.issue_title}\n"
                    f"Category: {instance.category.replace('_', ' ').title()}\n"
                    f"Priority: {instance.priority}\n"
                    f"Date Logged: {instance.date_logged.strftime('%Y-%m-%d %H:%M:%S') if instance.date_logged else 'N/A'}\n"
                    f"Resolution Date: {instance.resolution_date.strftime('%Y-%m-%d %H:%M:%S') if instance.resolution_date else 'N/A'}\n\n"
                    f"Issue Description:\n{instance.issue_description}\n\n"
                    f"Work Done:\n{instance.work_done or 'N/A'}\n\n"
                    f"Recommendation:\n{instance.recommendation or 'N/A'}\n\n"
                    f"If you have any further questions or require additional assistance, please do not hesitate to contact the IT department.\n\n"
                    f"Thank you for your cooperation.\n\n"
                    f"Best regards,\nIT Support Team\nParamount Bank"
                )
                # Send email to staff
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [staff_email],
                    fail_silently=True,
                )
                # Send the same email to IT support
                if it_support_email:
                    send_mail(
                        subject + f" (Issue reported by paramount staff member: {instance.submitted_by.first_name} {instance.submitted_by.last_name})",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [it_support_email],
                        fail_silently=True,
                    )

        # --- REAL-TIME WEBSOCKET NOTIFICATION (ON ISSUE RESOLVED) ---
        # Notify all dashboard clients via WebSocket about the issue resolution
        if hasattr(instance, 'status') and instance.status == 'completed':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    "type": "notify",
                    "message": {
                        "event": "issue_resolved",
                        "title": instance.issue_title,
                        "resolved_by": f"{staff.first_name} {staff.last_name}",
                        "resolution_date": instance.resolution_date.strftime('%Y-%m-%d %H:%M:%S') if instance.resolution_date else 'N/A',
                    }
                }
            )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # If full_details was set in perform_update, return it
        if hasattr(self, 'full_details'):
            response.data = self.full_details
        return response

# ---
# Comments:
# - Emails are sent in real time when a POST request is made (issue logged) and when a PUT request is made (issue resolved).
# - WebSocket notifications are also sent in real time for both events, so dashboard users see updates instantly.
# - All notification logic is commented for clarity and maintainability.
# - To test: use Django's test runner for backend logic, and a WebSocket client for real-time dashboard events.
# - These changes ensure prompt communication and visibility for both staff and IT support, supporting operational efficiency and compliance.
#
# How to run tests:
# 1. Run `python manage.py test` to execute all Django tests (including any in ReportLog/tests.py).
# 2. For WebSocket/manual testing, use a WebSocket client to connect to ws://<host>/ws/notifications/ and observe real-time events when issues are created or resolved.
#
# Purpose:
# - These changes enable real-time notifications for dashboard users, improve communication, and support audit/compliance needs for banking IT operations.
# - Email and WebSocket notifications ensure both staff and IT support are promptly informed.
#
# Requirements:
# - Django Channels and Redis must be installed and configured in settings.py and asgi.py.
# - See previous instructions for full setup.

# -daphne PARAMOUNT.asgi:application
