from rest_framework import serializers
from django.utils import timezone
from .models import ITIssue

class ITIssueSerializer(serializers.ModelSerializer):
    """
    Serializer for reading ITIssue records.

    Provides a complete representation of an IT issue, including all details and
    read-only fields. Used for GET/list/detail endpoints.

    Fields:
        id (UUID): Unique identifier for the issue (read-only)
        category (str): Category of the IT issue
        issue_title (str): Title of the issue
        issue_description (str): Detailed description
        priority (str): Priority level
        status (str): Current status (read-only)
        date_logged (datetime): When the issue was reported (read-only)
        associated_file (file): Optional file attachment
        resolution_date (datetime): When the issue was resolved (read-only)
        work_done (str): Actions taken (read-only)
        recommendation (str): Recommendations (read-only)
        method_of_logging (str): How the issue was reported
        submitted_by (UUID): Staff member who submitted the issue (read-only)
    """
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
    """
    Serializer for creating new ITIssue records.

    Used for POST endpoints to create a new IT issue. Only allows fields that
    should be set by the user at creation time.

    Fields:
        category (str): Category of the IT issue
        issue_title (str): Title of the issue
        issue_description (str): Detailed description
        priority (str): Priority level
        associated_file (file, optional): Optional file attachment
        method_of_logging (str): How the issue was reported
    """
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
    """
    Serializer for partial updates (PATCH) to ITIssue records.

    Allows staff to update only certain fields of an existing issue, such as
    category, title, description, priority, file, or method of logging.

    Fields:
        category (str): Category of the IT issue
        issue_title (str): Title of the issue
        issue_description (str): Detailed description
        priority (str): Priority level
        associated_file (file, optional): Optional file attachment
        method_of_logging (str): How the issue was reported
    """
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
    """
    Serializer for updating the status, work_done, and recommendation fields of an ITIssue.

    Used by privileged users or automated processes to update the status of an issue,
    add work notes, or provide recommendations. Handles automatic setting of
    resolution_date when status is set to 'completed'.

    Fields:
        status (str): New status for the issue
        work_done (str): Description of work performed
        recommendation (str): Recommendations for future prevention
    
    Special Logic:
        - Sets resolution_date if status is changed to 'completed' and not already set
        - Allows context injection of assigned_to and submitted_by for advanced workflows
    """
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
