# web/views.py
import os
import threading
from string import Template
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from web.models import AgentTask
from modules.orchestrator import execute_agent_task
from modules.personas import PERSONAS

def select_mode_view(request):
    """Step 1: Choose Operational Mode"""
    if request.method == 'POST':
        mode = request.POST.get('mode', 'ARTICURATOR')
        return redirect(f'/configure/?mode={mode}')
    return render(request, 'select_mode.html')

def config_form_view(request):
    """Step 2: Inputs and Agent Model Allocation"""
    # 1. Define your "Source of Truth" defaults here
    DEFAULT_MODE = 'ARTICURATOR'
    DEFAULT_LENGTH = '3'
    DEFAULT_TONE = 'Formal'
    DEFAULT_FORMAT = 'Plaintext'
    
    mode = request.GET.get('mode', DEFAULT_MODE)
    load_task_id = request.GET.get('load_task_id', '')

    # 2. LOAD PAST DATA FIRST (Ensures 'mode' is accurate before pulling prompts)
    config_context = {} 
    if load_task_id:
        try:
            past_task = AgentTask.objects.get(id=load_task_id)
            config_context = past_task.config_data
            mode = past_task.mode
        except AgentTask.DoesNotExist:
            pass
            
    # Load prompts using the finalized mode
    prompts = PERSONAS.get(mode, PERSONAS.get(DEFAULT_MODE))

    # 3. Handle POST
    if request.method == 'POST':
        mode = request.POST.get('mode', mode)
        
        # Use the SAME defaults here as in the GET logic
        length = request.POST.get('length', DEFAULT_LENGTH)
        tone = request.POST.get('tone', DEFAULT_TONE)
        output_format = request.POST.get('format', DEFAULT_FORMAT)        

        # Get the template dictionary for the selected mode
        mode_templates = PERSONAS.get(mode, PERSONAS.get(DEFAULT_MODE))
        
        # Build the config, substituting if it's the ARTICURATOR mode
        packed_config = {
            "model_agent_1": request.POST.get('model_agent_1'),
            "model_agent_2": request.POST.get('model_agent_2'),
            "model_agent_3": request.POST.get('model_agent_3'),
            "length": length,
            "tone": tone,
            "format": output_format,
        }
        
        # Fill in the prompts
        for key in ['agent_1', 'agent_2', 'agent_3']:
            template = mode_templates[key]
            if mode == 'ARTICURATOR':
                packed_config[f"prompt_{key}"] = template.substitute(length=length, tone=tone, output_format=output_format)
            else:
                packed_config[f"prompt_{key}"] = template.safe_substitute()
        
        # Handle the specific mode data
        if mode == 'ACLGENERATOR':
            packed_config["target_schema"] = request.POST.get('target_schema', '')
            if 'raw_csv' in request.FILES:
                csv_file = request.FILES['raw_csv']
                fs = FileSystemStorage(location='raw_uploads/')
                filename = fs.save(csv_file.name, csv_file)
                packed_config["uploaded_csv_path"] = os.path.join('raw_uploads/', filename)
            else:
                packed_config["uploaded_csv_path"] = config_context.get("uploaded_csv_path", "")
        else:
            packed_config["topic_brief"] = request.POST.get('topic_brief', '')
            packed_config["target_site_url"] = request.POST.get('target_site_url', '')

        # Create the task
        new_task = AgentTask.objects.create(
            mode=mode,
            status='PENDING',
            config_data=packed_config
        )
        
        # Thread hand-off
        execution_thread = threading.Thread(target=execute_agent_task, args=(new_task.id,))
        execution_thread.start()
        
        return redirect(f'/execution/{new_task.id}/')

    # 4. Fallback GET (Context now includes the loaded config strings!)
    display_length = config_context.get("length", DEFAULT_LENGTH)
    display_tone = config_context.get("tone", DEFAULT_TONE)
    display_format = config_context.get("format", DEFAULT_FORMAT)

    rendered_prompts = {
        k: v.safe_substitute(length=display_length, tone=display_tone, output_format=display_format) 
        for k, v in prompts.items()
    }
    
    context = {
        'mode': mode,
        'prompts': rendered_prompts,  # Fixed: Passing clean strings, not Template objects
        'config': config_context 
    }
    return render(request, 'config_form.html', context)

def execution_page_view(request, task_id):
    """Step 3: Real-Time Telemetry Pipeline Screen Rendering"""
    task = get_object_or_404(AgentTask, id=task_id)
    # Grab the selected format, default to plaintext if it doesn't exist
    selected_format = task.config_data.get('format', 'Plaintext')
    
    context = {
        'task': task,
        'output_format': selected_format
    }
    return render(request, 'execution.html', context)

def get_task_logs_api(request, task_id):
    """Live Telemetry Log Stream Feed Polling Endpoint"""
    task = get_object_or_404(AgentTask, id=task_id)
    return JsonResponse({
        "status": task.status,
        "logs": task.config_data.get("execution_logs", []),
        "artifact": task.config_data.get("final_artifact", "") if task.status == "SUCCESS" else ""
    })

def dashboard_view(request):
    """Task Control Center History Grid Layout"""
    tasks = AgentTask.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'tasks': tasks})

# Append to web/views.py

def edit_config_view(request, task_id):
    """Redirects to config form with historical context loaded for editing"""
    past_task = get_object_or_404(AgentTask, id=task_id)
    return redirect(f'/configure/?mode={past_task.mode}&load_task_id={past_task.id}')

def rerun_task_view(request, task_id):
    """Instantly clones the configuration and triggers the orchestrator execution"""
    past_task = get_object_or_404(AgentTask, id=task_id)
    new_task = AgentTask.objects.create(
        mode=past_task.mode,
        status='PENDING',
        config_data=past_task.config_data.copy()
    )
    # Clear out old execution metrics/logs for the new run window
    if "execution_logs" in new_task.config_data:
        new_task.config_data["execution_logs"] = []
    if "final_artifact" in new_task.config_data:
        del new_task.config_data["final_artifact"]
    new_task.save()
    
    execute_agent_task(new_task.id)
    return redirect(f'/execution/{new_task.id}/')

def duplicate_task_view(request, task_id):
    """Redirects to form configuration with historical data replicated as a clean template"""
    past_task = get_object_or_404(AgentTask, id=task_id)
    return redirect(f'/configure/?mode={past_task.mode}&load_task_id={past_task.id}')

def delete_task_view(request, task_id):
    """Permanently removes task execution records from the database state"""
    task = get_object_or_404(AgentTask, id=task_id)
    task.delete()
    return redirect('dashboard')

def task_status_api(request, task_id):
    """Fallback status API endpoint to support legacy naming variations in templates"""
    task = get_object_or_404(AgentTask, id=task_id)
    return JsonResponse({
        "status": task.status,
        "logs": "\n".join(task.config_data.get("execution_logs", [])) 
                if isinstance(task.config_data.get("execution_logs"), list) 
                else task.config_data.get("execution_logs", "")
    })