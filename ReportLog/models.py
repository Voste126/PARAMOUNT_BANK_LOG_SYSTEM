from django.db import models
from Staff.models import Staff

class ITIssue(models.Model):
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
    ]
    METHOD_CHOICES = [
        ('gmail', 'Gmail'),
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
        # Set resolution_date automatically if status is completed and not already set
        if self.status == 'completed' and self.resolution_date is None:
            from django.utils import timezone
            self.resolution_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.issue_title
