from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ITIssue
from .serializer import ITIssueSerializer, ITIssueCreateSerializer, ITIssuePatchSerializer
from Staff.models import Staff

class ITIssueCreateView(generics.CreateAPIView):
    queryset = ITIssue.objects.all()
    serializer_class = ITIssueCreateSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

class ITIssuePatchView(generics.UpdateAPIView):
    queryset = ITIssue.objects.all()
    serializer_class = ITIssuePatchSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ITIssue.objects.filter(submitted_by=self.request.user)

class ITIssueDeleteView(generics.DestroyAPIView):
    queryset = ITIssue.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ITIssue.objects.filter(submitted_by=self.request.user)
