from rest_framework import serializers
from django.utils import timezone
from .models import ITIssue

class ITIssueSerializer(serializers.ModelSerializer):
    submitted_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ITIssue
        # full set of fields for read
        fields = [
            'id', 'category', 'issue_title', 'issue_description', 'priority', 'status', 'date_logged',
            'associated_file', 'resolution_date', 'work_done',
            'recommendation', 'method_of_logging', 'submitted_by'
        ]
        read_only_fields = [
            'id', 'status', 'date_logged',
            'resolution_date', 'work_done', 'recommendation', 'submitted_by'
        ]


class ITIssueCreateSerializer(serializers.ModelSerializer):
    associated_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ITIssue
        # only the writable fields on create
        fields = [
            'category',
            'issue_title',
            'issue_description',
            'priority',
            'associated_file',
            'method_of_logging',
        ]


class ITIssuePatchSerializer(serializers.ModelSerializer):
    associated_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ITIssue
        # fields you allow staff to patch via your custom PUT endpoint
        fields = [
            'category',
            'issue_title',
            'issue_description',
            'priority',
            'associated_file',
            'method_of_logging',
        ]


class ITIssueUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITIssue
        fields = [
            'status',
            'work_done',
            'recommendation',
        ]

    def update(self, instance, validated_data):
        # update status/work_done/recommendation
        instance.status = validated_data.get('status', instance.status)
        instance.work_done = validated_data.get('work_done', instance.work_done)
        instance.recommendation = validated_data.get('recommendation', instance.recommendation)

        # set resolution_date on completion
        if instance.status == 'completed' and not instance.resolution_date:
            instance.resolution_date = timezone.now()

        # allow view to inject assigned_to/submitted_by via .context
        assigned_to  = self.context.get('assigned_to')
        submitted_by = self.context.get('submitted_by')
        if assigned_to:
            instance.assigned_to = assigned_to
        if submitted_by:
            instance.submitted_by = submitted_by

        instance.save()
        return instance
