# web/utils.py
from .models import AgentTask
from django.utils import timezone

def append_task_log(task_id, message):
    """
    Fetches the specified AgentTask and appends a timestamped log line 
    directly into its config_data JSON dictionary, saving it instantly.
    """
    if not task_id:
        return
        
    try:
        task = AgentTask.objects.get(id=task_id)
        if "execution_logs" not in task.config_data:
            task.config_data["execution_logs"] = []
            
        timestamp = timezone.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        
        task.config_data["execution_logs"].append(log_line)
        task.save(update_fields=['config_data'])
    except AgentTask.DoesNotExist:
        pass