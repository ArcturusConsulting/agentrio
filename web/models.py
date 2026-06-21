from django.db import models

class AgentTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    MODE_CHOICES = [
        ('ACL', 'ACL Generator'),
        ('CURATOR', 'ArtiCurator'),
    ]

    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    output_file_path = models.CharField(max_length=500, null=True, blank=True)
    log_output = models.TextField(null=True, blank=True)
    config_data = models.JSONField(default=dict, blank=True)

def __str__(self):
        # Safely extract the model name from our JSON configuration data, 
        # defaulting to 'Default LLM' if it hasn't been set yet.
        selected_model = self.config_data.get('model', 'Default LLM')
        return f"Task {self.id} - {self.mode} [{selected_model}] ({self.status})"