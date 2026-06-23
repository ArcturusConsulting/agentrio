# web/utils.py
import calendar
from datetime import datetime, timedelta

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


def get_token_safe_calendar_manifest() -> str:
    """
    Generates a pristine, line-by-line chronological manifest mapping 
    dates directly to weekdays, covering exactly three full calendar months.
    """
    now = datetime.utcnow()
    first_this_month = datetime(now.year, now.month, 1)
    
    # 1. Effortlessly sample the three target months using basic shifts
    target_months = [
        first_this_month - timedelta(days=1),  # Shifts securely into previous month
        first_this_month,                      # Current month
        first_this_month + timedelta(days=32)  # Shifts securely into next month
    ]
    
    cal = calendar.Calendar()
    lines = ["=== CRITICAL CHRONOLOGICAL CALENDAR TRUTH MATRIX ==="]
    lines.append(f"Current System Execution Context: {now.strftime('%B %d, %Y, %H:%M UTC')}\n")
    
    # 2. Grab the days month-by-month and append them
    for target in target_months:
        # itermonthdates natively extracts every single day in that specific month
        for day in cal.itermonthdates(target.year, target.month):
            # Filter out overlapping padding days from neighboring weeks
            if day.month == target.month:
                lines.append(f"- {day.strftime('%B %d, %Y')} is a {day.strftime('%A')}")
                
    lines.append("====================================================")
    return "\n".join(lines)