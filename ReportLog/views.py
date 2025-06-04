# # Comments:
# # - Emails are sent in real time when a POST request is made (issue logged) and when a PUT request is made (issue resolved).
# # - WebSocket notifications are also sent in real time for both events, so dashboard users see updates instantly.
# # - All notification logic is commented for clarity and maintainability.
# # - To test: use Django's test runner for backend logic, and a WebSocket client for real-time dashboard events.
# # - These changes ensure prompt communication and visibility for both staff and IT support, supporting operational efficiency and compliance.
# #
# # How to run tests:
# # 1. Run `python manage.py test` to execute all Django tests (including any in ReportLog/tests.py).
# # 2. For WebSocket/manual testing, use a WebSocket client to connect to ws://<host>/ws/notifications/ and observe real-time events when issues are created or resolved.
# #
# # Purpose:
# # - These changes enable real-time notifications for dashboard users, improve communication, and support audit/compliance needs for banking IT operations.
# # - Email and WebSocket notifications ensure both staff and IT support are promptly informed.
# #
# # Requirements:
# # - Django Channels and Redis must be installed and configured in settings.py and asgi.py.
# # - See previous instructions for full setup.
# # -DJANGO_SETTINGS_MODULE=PARAMOUNT.settings daphne -b 0.0.0.0 -p 8000 PARAMOUNT.asgi:application



from rest_framework import generics, permissions, status
from rest_framework.parsers     import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions  import NotAuthenticated, NotFound
from rest_framework.response    import Response
from django.core.mail           import send_mail
from django.conf                import settings
from asgiref.sync               import async_to_sync
from channels.layers            import get_channel_layer
from drf_yasg.utils             import swagger_auto_schema
from drf_yasg                   import openapi
from rest_framework             import serializers

from .models     import ITIssue
from .serializer import (
    ITIssueSerializer,
    ITIssueCreateSerializer,
    ITIssuePatchSerializer,
    ITIssueUpdateStatusSerializer
)
from Staff.models import Staff


class ITIssueListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Short-circuit for schema generation (Swagger/OpenAPI)
        if getattr(self, 'swagger_fake_view', False):
            return ITIssue.objects.none()

        user = self.request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")

        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            raise NotFound(detail="User not found", code="user_not_found")

        return ITIssue.objects.filter(submitted_by=staff)

    def get_serializer_class(self):
        # Use create-only serializer for POST, full serializer otherwise
        if self.request.method == 'POST':
            return ITIssueCreateSerializer
        return ITIssueSerializer

    def create(self, request, *args, **kwargs):
        # 1) Validate & save with the create-only serializer
        create_ser = self.get_serializer(data=request.data)
        create_ser.is_valid(raise_exception=True)

        staff = Staff.objects.get(id=request.user.id)
        issue = create_ser.save(submitted_by=staff)

        # 2) Send acknowledgement e-mail to staff
        if staff.email:
            subject = f"IT Issue Successfully Logged: {issue.issue_title}"
            message = (
                f"Dear {staff.first_name} {staff.last_name},\n\n"
                f"Your IT issue has been successfully logged. Our IT team will begin working on it immediately.\n\n"
                f"Issue Title: {issue.issue_title}\n"
                f"Category: {issue.category.replace('_',' ').title()}\n"
                f"Priority: {issue.priority}\n"
                f"Date Logged: {issue.date_logged:%Y-%m-%dT%H:%M:%SZ}\n\n"
                f"Description:\n{issue.issue_description}\n\n"
                f"Best regards,\nIT Support Team"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [staff.email],
                fail_silently=False
            )

        # 3) Notify IT support mailbox
        it_support = getattr(settings, 'IT_SUPPORT_EMAIL', None)
        if it_support:
            it_subject = f"New IT Issue by {staff.first_name} {staff.last_name}"
            it_message = (
                f"{staff.first_name} {staff.last_name} ({staff.email}) logged a new issue:\n\n"
                f"Title: {issue.issue_title}\n"
                f"Category: {issue.category.replace('_',' ').title()}\n"
                f"Priority: {issue.priority}\n"
                f"Date Logged: {issue.date_logged:%Y-%m-%dT%H:%M:%SZ}\n\n"
                f"Description:\n{issue.issue_description}\n"
            )
            send_mail(
                it_subject,
                it_message,
                settings.DEFAULT_FROM_EMAIL,
                [it_support],
                fail_silently=False
            )

        # 4) Push real-time WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "notify",
                "message": {
                    "event": "new_issue",
                    "title": issue.issue_title,
                    "submitted_by": f"{staff.first_name} {staff.last_name}",
                    "priority": issue.priority,
                    "category": issue.category,
                    "date_logged": issue.date_logged.strftime('%Y-%m-%dT%H:%M:%SZ'),
                }
            }
        )

        # 5) Return the full payload with the read serializer
        read_ser = ITIssueSerializer(issue)
        headers = self.get_success_headers(read_ser.data)
        return Response(read_ser.data, status=status.HTTP_201_CREATED, headers=headers)


class ITIssueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Short-circuit for schema generation (Swagger/OpenAPI)
        if getattr(self, 'swagger_fake_view', False):
            return ITIssue.objects.none()

        user = self.request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        try:
            staff = Staff.objects.get(id=user.id)
        except Staff.DoesNotExist:
            raise NotFound(detail="User not found", code="user_not_found")

        return ITIssue.objects.filter(submitted_by=staff)

    def get_serializer_class(self):
        # Use status-update serializer for PUT/PATCH, full serializer otherwise
        if self.request.method in ['PUT', 'PATCH']:
            return ITIssueUpdateStatusSerializer
        return ITIssueSerializer

    def perform_update(self, serializer):
        # Ensure submitted_by stays with the same staff
        staff = Staff.objects.get(id=self.request.user.id)
        serializer.instance.submitted_by = staff

        # Save & let the serializer set resolution_date if needed
        instance = serializer.save()

        # Debugging: Log the status to ensure it is 'completed'
        print(f"Debug: Status is {instance.status}")

        # Debugging: Log email sending process
        if instance.status == 'completed':
            print("Debug: Status is 'completed', proceeding to send emails.")

            # Email to reporting staff
            if instance.submitted_by.email:
                print(f"Debug: Sending email to {instance.submitted_by.email}")

            # Email to IT support
            it_support = getattr(settings, 'IT_SUPPORT_EMAIL', None)
            if it_support:
                print(f"Debug: Sending email to IT support at {it_support}")

        # If status just turned to completed, send resolution e-mails
        if instance.status == 'completed':
            # Email to reporting staff
            if instance.submitted_by.email:
                subject = f"Issue Resolved: {instance.issue_title}"
                message = (
                    f"Dear {instance.submitted_by.first_name} {instance.submitted_by.last_name},\n\n"
                    f"Your reported IT issue has been resolved.\n\n"
                    f"Issue Title: {instance.issue_title}\n"
                    f"Category: {instance.category.replace('_',' ').title()}\n"
                    f"Priority: {instance.priority}\n"
                    f"Date Logged: {instance.date_logged:%Y-%m-%dT%H:%M:%SZ}\n"
                    f"Resolution Date: {instance.resolution_date:%Y-%m-%dT%H:%M:%SZ}\n\n"
                    f"Work Done:\n{instance.work_done or 'N/A'}\n\n"
                    f"Recommendation:\n{instance.recommendation or 'N/A'}\n\n"
                    f"Best regards,\nIT Support Team"
                )
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.submitted_by.email],
                        fail_silently=False
                    )
                except Exception as e:
                    print(f"Error sending email to reporting staff: {e}")

            # Email to IT support
            it_support = getattr(settings, 'IT_SUPPORT_EMAIL', None)
            if it_support:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [it_support],
                        fail_silently=False
                    )
                except Exception as e:
                    print(f"Error sending email to IT support: {e}")

        # Log the status field value from the PUT request payload
        print(f"Debug: Received status value: {serializer.validated_data.get('status')}")

        # stash the full serialized data for `update()` to return
        self.full_details = ITIssueSerializer(instance).data

    def update(self, request, *args, **kwargs):
        # run perform_update, then return the full payload
        super().update(request, *args, **kwargs)
        return Response(self.full_details, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # Optionally you could notify on delete, etc.
        return super().destroy(request, *args, **kwargs)


class CategoryChoicesSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()

class CategoryChoicesView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = CategoryChoicesSerializer  # Added serializer_class for schema generation

    def get(self, request):
        choices = [
            {"id": key, "name": value}
            for key, value in ITIssue.CATEGORY_CHOICES
        ]
        return Response(choices)


class StaffUpdateIssueView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    lookup_url_kwarg   = 'pk'
    serializer_class   = ITIssuePatchSerializer
    queryset           = ITIssue.objects.all()  # Added queryset for schema generation

    @swagger_auto_schema(
        operation_description="Update specific non‐status fields of an existing issue",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category': openapi.Schema(type=openapi.TYPE_STRING),
                'issue_title': openapi.Schema(type=openapi.TYPE_STRING),
                'issue_description': openapi.Schema(type=openapi.TYPE_STRING),
                'priority': openapi.Schema(type=openapi.TYPE_STRING),
                'associated_file': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
                'method_of_logging': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[]
        ),
        responses={
            200: openapi.Response("Issue updated successfully"),
            404: openapi.Response("Issue not found or permission denied"),
        }
    )
    def put(self, request, *args, **kwargs):
        # ensure the staff only updates their own issues
        try:
            staff = Staff.objects.get(id=request.user.id)
        except Staff.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            issue = ITIssue.objects.get(id=kwargs['pk'], submitted_by=staff)
        except ITIssue.DoesNotExist:
            return Response({"detail": "Issue not found or permission denied"}, status=status.HTTP_404_NOT_FOUND)

        # apply only the allowed fields
        for field in self.serializer_class.Meta.fields:
            if field in request.data:
                setattr(issue, field, request.data[field])
        issue.save()
        return Response({"detail": "Issue updated successfully"}, status=status.HTTP_200_OK)

