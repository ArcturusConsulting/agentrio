# modules/orchestrator.py
import sys
import os

# Ensure the root project directory is in the Python path to clear import warnings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Standard top-level architectural imports
from modules.acl_generator import run_acl_agent_graph
from modules.articurator import run_articurator_graph
from web.models import AgentTask
from web.utils import append_task_log 

def execute_agent_task(task_id):
    """
    Orchestration state machine execution manager. Handles switching tasks from
    PENDING -> RUNNING -> SUCCESS or FAILED, routing to the correct agent engine graph.
    Uses top-level imports and a functional callback wrapper to keep graphs pure Python.
    """
    try:
        task = AgentTask.objects.get(id=task_id)
    except AgentTask.DoesNotExist:
        return

    task.status = 'RUNNING'
    task.save(update_fields=['status'])
    
    # Define a clean runner-level callback function that maps pure string logs back to the database
    def log_callback(message):
        append_task_log(task.id, message)
    
    try:
        if task.mode == 'ACL':
            artifact = run_acl_agent_graph(task.config_data, logger_callback=log_callback)
        else:
            artifact = run_articurator_graph(task.config_data, logger_callback=log_callback)
            
        task.status = 'SUCCESS'
        task.config_data["final_artifact"] = artifact
        task.save(update_fields=['status', 'config_data'])
        
    except Exception as e:
            import traceback
            print("\n!!! GRAPH EXECUTION CRASH DETECTED !!!")
            traceback.print_exc()  # This forces the full error stack to print directly to your terminal screen
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            
            task.status = 'FAILED'
            # Copy the dictionary explicitly to ensure Django registers the internal mutation layout change
            updated_config = dict(task.config_data)
            updated_config["error_message"] = str(e)
            updated_config["execution_logs"] = [f"[CRITICAL ERROR] Graph aborted: {str(e)}"]
            
            task.config_data = updated_config
            task.save() # Save the whole object to force database sync updates