from rest_framework import serializers
from .models import ITIssue

class ITIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITIssue
        fields = [
            'id', 'category', 'issue_title', 'issue_description', 'priority', 'status', 'date_logged',
            'assigned_to', 'associated_file', 'resolution_date', 'work_done',
            'recommendation', 'method_of_logging', 'submitted_by'
        ]
        read_only_fields = ['status', 'date_logged', 'resolution_date', 'work_done', 'recommendation', 'assigned_to', 'submitted_by']

class ITIssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITIssue
        fields = [
            'category', 'issue_title', 'issue_description', 'priority', 'associated_file', 'method_of_logging'
        ]

class ITIssuePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITIssue
        fields = [
            'category', 'issue_title', 'issue_description', 'priority', 'associated_file', 'method_of_logging'
        ]
