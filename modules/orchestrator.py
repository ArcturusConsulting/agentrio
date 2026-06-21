# modules/orchestrator.py
import os
import logging
from datetime import datetime

# Configure a clean console logger for tracking our multi-agent boundaries
logger = logging.getLogger("agentrio.orchestrator")

def execute_agent_task(task_id):
    """
    The Central Orchestration Loop. Takes a database task ID, transitions its state,
    routes it to the correct multi-agent sub-graph, and logs state transitions.
    """
    # 1. Lazy import Django models to avoid early initialization circular errors
    from web.models import AgentTask
    
    try:
        task = AgentTask.objects.get(id=task_id)
    except AgentTask.DoesNotExist:
        logger.error(f"Orchestrator Failure: Task ID #{task_id} not found in SQLite.")
        return False

    logger.info(f"===> [ORCHESTRATOR] Intercepted Task #{task.id} [{task.mode}]")
    
    # 2. Advance state to RUNNING
    task.status = 'RUNNING'
    task.save()

    # 3. Extract our isolated Anti-Corruption Layer configurations matching Step 2 Form
    config = task.config_data

    # Set up our local output paths based on the design rules
    if task.mode == 'ACL':
        artifacts_dir = os.path.join(os.getcwd(), 'outputs', 'acl')
    else:
        artifacts_dir = os.path.join(os.getcwd(), 'outputs', 'curator')
        
    os.makedirs(artifacts_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"artifact_{task.mode}_{task.id}_{timestamp}.md"
    output_path = os.path.join(artifacts_dir, output_filename)

    try:
        # 4. Route payload execution to the specific multi-agent micro-graphs passing full context
        if task.mode == 'ACL':
            from modules.acl_generator import run_acl_agent_graph
            logger.info("      Routing execution token to [ACL Generator Graph Engine]...")
            execution_log, artifact_content = run_acl_agent_graph(config)
            
        elif task.mode == 'CURATOR':
            from modules.articurator import run_articurator_graph
            logger.info("      Routing execution token to [ArtiCurator Loop Engine]...")
            execution_log, artifact_content = run_articurator_graph(config)
            
        else:
            raise ValueError(f"Unknown Operational Orchestrator Mode: {task.mode}")

        # 5. Commit generated physical artifact payload to storage disk
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(artifact_content)

        # 6. Capture full execution trace matching the template key, and finish task
        task.status = 'SUCCESS'
        task.output_file_path = output_path
        task.config_data['execution_logs'] = execution_log
        task.save()
        
        logger.info(f"===> [ORCHESTRATOR] Task #{task.id} completed successfully. Artifact saved.")
        return True

    except Exception as e:
        logger.error(f"!!! [ORCHESTRATOR ERROR] Task #{task.id} Failed: {str(e)}")
        task.status = 'FAILED'
        task.config_data['execution_logs'] = f"Execution Interrupted: {str(e)}"
        task.save()
        return False