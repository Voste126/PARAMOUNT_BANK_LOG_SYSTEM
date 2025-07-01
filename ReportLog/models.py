from django.db import models
from Staff.models import Staff
import uuid

class ITIssue(models.Model):
    """
    Model representing IT-related issues reported by staff members in the Paramount Bank system.
    
    This model tracks and manages all IT issues including software problems, hardware issues,
    network concerns, and banking system-related problems. Each issue is logged with detailed
    information about its nature, priority, status, and resolution.

    Attributes:
        id (UUIDField): Unique identifier for the issue using UUID4
        
        category (CharField): Type of the IT issue
            Choices:
            - internet_banking: Issues related to internet banking platform
            - mobile_banking: Mobile banking application issues
            - br_net: BR.NET system-related problems
            - network_issue: Network connectivity problems
            - hardware_issue: Physical hardware-related issues
            - others: Miscellaneous issues
        
        issue_title (CharField): Brief title describing the issue
        issue_description (TextField): Detailed description of the problem
        
        priority (CharField): Urgency level of the issue
            Choices:
            - Critical: Requires immediate attention
            - High: Urgent but not critical
            - Normal: Standard priority
            - Low: Can be addressed when resources are available
        
        status (CharField): Current state of the issue
            Choices:
            - new: Newly reported issue
            - in-progress: Currently being worked on
            - duplicate: Similar to an existing issue
            - follow-up: Requires additional follow-up
            - completed: Issue has been resolved
            - unresolved: Cannot be resolved at this time
        
        date_logged (DateTimeField): Timestamp when the issue was reported
        associated_file (FileField): Any relevant files or screenshots
        resolution_date (DateTimeField): When the issue was resolved
        work_done (TextField): Description of actions taken to resolve the issue
        recommendation (TextField): Suggestions to prevent similar issues
        
        method_of_logging (CharField): How the issue was reported
            Choices:
            - email: Reported via email
            - call: Reported via phone call
        
        submitted_by (ForeignKey): Staff member who reported the issue
    
    Methods:
        save(): Overridden to automatically set resolution_date when status changes to 'completed'
        __str__(): Returns the issue_title for string representation
    
    Relationships:
        - Each issue is associated with one Staff member (submitted_by)
        - Staff can access their submitted issues via the 'submitted_issues' related name
    
    Example:
        >>> issue = ITIssue.objects.create(
        ...     category='network_issue',
        ...     issue_title='Network Down in Branch',
        ...     priority='Critical',
        ...     method_of_logging='call',
        ...     submitted_by=staff_member
        ... )
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    PRIORITY_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Normal', 'Normal'),
        ('Low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in-progress', 'In Progress'),
        ('duplicate', 'Duplicate'),
        ('follow-up', 'Follow Up'),
        ('completed', 'Completed'),
        ('unresolved', 'Unresolved'),
    ]

    METHOD_CHOICES = [
        ('email', 'Email'),
        ('call', 'Call'),
    ]

    CATEGORY_CHOICES = [
        ('internet_banking', 'Internet Banking'),
        ('mobile_banking', 'Mobile Banking'),
        ('br_net', 'BR. NET'),
        ('network_issue', 'Network Issue'),
        ('hardware_issue', 'Hardware Issue'),
        ('others', 'Others'),
    ]

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES,default='others')
    issue_title = models.CharField(max_length=255)
    issue_description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    date_logged = models.DateTimeField(auto_now_add=True)
    associated_file = models.FileField(upload_to='issue_files/', blank=True, null=True)
    resolution_date = models.DateTimeField(blank=True, null=True)
    work_done = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    method_of_logging = models.CharField(max_length=10, choices=METHOD_CHOICES)
    submitted_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='submitted_issues')

    """
    Each Staff (user) can submit many ITIssue records via the 'submitted_by' ForeignKey.
    Use related_name='submitted_issues' to access all issues submitted by a staff member.
    """

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically set resolution_date when an issue is completed.
        
        When the status changes to 'completed' and no resolution_date is set, this method
        will automatically set the resolution_date to the current timestamp before saving.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Set resolution_date automatically if status is completed and not already set
        if self.status == 'completed' and self.resolution_date is None:
            from django.utils import timezone
            self.resolution_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the ITIssue.
        
        Returns:
            str: The issue title for easy identification
        """
        return self.issue_title
