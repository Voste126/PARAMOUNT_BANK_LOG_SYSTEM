from rest_framework import generics, permissions
from .models import ITIssue
from .serializer import ITIssueSerializer, ITIssueCreateSerializer, ITIssueUpdateStatusSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotAuthenticated

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

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # If full_details was set in perform_update, return it
        if hasattr(self, 'full_details'):
            response.data = self.full_details
        return response
