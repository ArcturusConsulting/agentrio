import os
import json
import logging
from datetime import datetime
from django.utils import timezone

# Configure a clean console logger for tracking our multi-agent boundaries
logger = logging.getLogger("agentrio.orchestrator")
logging.basicConfig(level=logging.INFO)

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

    # 3. Extract our isolated Anti-Corruption Layer configurations
    config = task.config_data
    provider = config.get('provider', 'default')
    model_name = config.get('model', 'Default LLM')
    prompt_input = config.get('prompt_input', '')

    logger.info(f"      Target Provider: {provider.upper()} | Model: {model_name}")

    # Create a local directory structure for tracking output artifacts safely
    artifacts_dir = os.path.join(os.getcwd(), 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"artifact_{task.mode}_{task.id}_{timestamp}.md"
    output_path = os.path.join(artifacts_dir, output_filename)

    try:
        # 4. Route payload execution to the specific multi-agent micro-graphs
        if task.mode == 'ACL':
            from modules.acl_generator import run_acl_agent_graph
            logger.info("      Routing execution token to [ACL Generator Graph Engine]...")
            execution_log, artifact_content = run_acl_agent_graph(provider, model_name, prompt_input)
            
        elif task.mode == 'CURATOR':
            from modules.articurator import run_articurator_graph
            logger.info("      Routing execution token to [ArtiCurator Loop Engine]...")
            execution_log, artifact_content = run_articurator_graph(provider, model_name, prompt_input)
            
        else:
            raise ValueError(f"Unknown Operational Orchestrator Mode: {task.mode}")

        # 5. Commit generated physical artifact payload to storage disk
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(artifact_content)

        # 6. Capture full execution trace and transition state to SUCCESS
        task.status = 'SUCCESS'
        task.output_file_path = output_path
        # Stashing raw execution log traces directly inside the JSON config metadata layer
        task.config_data['execution_trace_log'] = execution_log
        task.save()
        
        logger.info(f"===> [ORCHESTRATOR] Task #{task.id} completed successfully. Artifact saved.")
        return True

    except Exception as e:
        logger.error(f"!!! [ORCHESTRATOR ERROR] Task #{task.id} Failed: {str(e)}")
        task.status = 'FAILED'
        task.config_data['execution_failure_reason'] = str(e)
        task.save()
        return False