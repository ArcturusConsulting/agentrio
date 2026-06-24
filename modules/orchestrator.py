# modules/orchestrator.py
import sys
import os
from datetime import datetime

# Ensure the root project directory is in the Python path to clear import warnings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Standard top-level architectural imports
from modules.gateway import fetch_live_market_data
from modules.gateway import fetch_target_site_content
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
        if task.mode == 'ACLGENERATOR':
            artifact = run_acl_agent_graph(task.config_data, logger_callback=log_callback)
        else:
            # --- INTERCEPT FOR ARTICURATOR: MULTI-VECTOR RESEARCH LAYER ---        
            topic = task.config_data.get("topic_brief", "")
            target_url = task.config_data.get("target_site_url", "")
            
            # Generates a granular timestamp like: "June 24, 2026, 21:46 UTC"
            current_date_str = datetime.now().strftime("%B %d, %Y, %H:%M UTC") 

            # Vector A: News/Topic Research for Analisa
            live_context = fetch_live_market_data(topic)
            
            # Vector B: Target Website Analysis for Writus
            site_context = fetch_target_site_content(target_url)
            
            # FORCE DJANGO TO REGISTER THE DICTIONARY MUTATION BY CREATING A FRESH COPY
            updated_config = dict(task.config_data)
            updated_config["live_research_data"] = live_context
            updated_config["target_site_context"] = site_context
            updated_config["current_system_date"] = current_date_str # <-- INJECT THE DATE ANCHOR HERE

            task.config_data = updated_config
            task.save() # Forces full synchronous database payload write

            artifact = run_articurator_graph(task.config_data, logger_callback=log_callback)        
        
        # 💡 THE ATOMIC FIX: Update the database record directly by ID query.
        # This writes ONLY the status change and final_artifact string down to SQLite,
        # preventing the stale in-memory task dictionary from wiping out your logs!
        AgentTask.objects.filter(id=task_id).update(
            status='SUCCESS',
            config_data={
                **task.config_data,
                "final_artifact": artifact
            }
        )
        
    except Exception as e:
        import traceback
        print("\n!!! GRAPH EXECUTION CRASH DETECTED !!!")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        
        # Crash Protection: Safely isolate the FAILED status update using atomic updates as well
        try:
            current_task = AgentTask.objects.get(id=task_id)
            failed_config = dict(current_task.config_data)
            failed_config["error_message"] = str(e)
            
            AgentTask.objects.filter(id=task_id).update(
                status='FAILED',
                config_data=failed_config
            )
        except Exception as nested_err:
            print(f"[CRITICAL ERROR] Failed to record task failure state: {nested_err}")