from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ITIssue
from .serializer import ITIssueSerializer, ITIssueCreateSerializer, ITIssuePatchSerializer
from Staff.models import Staff

# A staff who has a JWT access token hence authenticated can create an issue in the API
class ITIssueCreateView(generics.CreateAPIView):
    queryset = ITIssue.objects.all()
    serializer_class = ITIssueCreateSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ITIssue.objects.none()
        try:
            staff_instance = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return ITIssue.objects.none()
        return ITIssue.objects.filter(submitted_by=staff_instance)

class ITIssuePatchView(generics.UpdateAPIView):
    queryset = ITIssue.objects.all()
    serializer_class = ITIssuePatchSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ITIssue.objects.none()
        try:
            staff_instance = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return ITIssue.objects.none()
        return ITIssue.objects.filter(submitted_by=staff_instance)

class ITIssueDeleteView(generics.DestroyAPIView):
    queryset = ITIssue.objects.all()
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ITIssue.objects.none()
        try:
            staff_instance = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return ITIssue.objects.none()
        return ITIssue.objects.filter(submitted_by=staff_instance)
