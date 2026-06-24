# web/models.py
from django.db import models

class AgentTask(models.Model):
    """
    Orchestration task container for tracking state transitions and multi-agent logs.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    mode = models.CharField(max_length=50)  # e.g., 'ACL' or 'CURATOR'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    config_data = models.JSONField(default=dict, blank=True)  # Stores agent matrix and telemetry logs
    output_file_path = models.CharField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    execution_logs = models.TextField(default="")

    def __str__(self):
        return f"Task #{self.id} ({self.mode}) - {self.status}"