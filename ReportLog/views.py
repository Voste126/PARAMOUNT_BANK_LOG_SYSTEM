from rest_framework import generics, permissions
from .models import ITIssue
from .serializer import ITIssueSerializer, ITIssueCreateSerializer, ITIssueUpdateStatusSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from django.conf import settings

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
        serializer.save(submitted_by=staff)

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

        # Send email notification if issue is resolved (status is 'completed')
        if hasattr(instance, 'status') and instance.status == 'completed':
            staff_email = instance.submitted_by.email if instance.submitted_by else None
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
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [staff_email],
                    fail_silently=True,
                )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # If full_details was set in perform_update, return it
        if hasattr(self, 'full_details'):
            response.data = self.full_details
        return response
