# agentrio/web/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from .models import AgentTask, PromptTemplate
from modules.orchestrator import execute_agent_task  # Your pure Python engine loop

# ==========================================
# BRANCH 1: THREE-STEP WIZARD
# ==========================================

def select_mode_view(request):
    """Step 1: Select Processing Engine Mode (select_mode.html)"""
    return render(request, 'select_mode.html')


def config_form_view(request):
    """Step 2: Inputs, CSV files, prompt editors (CRUD), and model matrices (config_form.html)"""
    mode = request.GET.get('mode', 'ACL')  # Fallback to ACL if not specified
    
    if request.method == 'POST':
        mode = request.POST.get('mode', mode)
        
        # 1. Handle Mode-Specific Inputs & File Uploads
        packed_config = {
            "model_agent_1": request.POST.get('model_agent_1'),
            "model_agent_2": request.POST.get('model_agent_2'),
            "model_agent_3": request.POST.get('model_agent_3'),
            "prompt_agent_1": request.POST.get('prompt_agent_1'),
            "prompt_agent_2": request.POST.get('prompt_agent_2'),
            "prompt_agent_3": request.POST.get('prompt_agent_3'),
        }
        
        if mode == 'ACL':
            packed_config["target_schema"] = request.POST.get('target_schema', '')
            # Save physical .csv to your dedicated raw_uploads folder
            if 'raw_csv' in request.FILES:
                csv_file = request.FILES['raw_csv']
                fs = FileSystemStorage(location='raw_uploads/')
                filename = fs.save(csv_file.name, csv_file)
                packed_config["uploaded_csv_path"] = os.path.join('raw_uploads/', filename)
        else:
            packed_config["topic_brief"] = request.POST.get('topic_brief', '')

        # 2. Persist the State into SQLite
        new_task = AgentTask.objects.create(
            mode=mode,
            status='PENDING',
            config_data=packed_config
        )
        
        # 3. Hand over execution to the background processing graph
        execute_agent_task(new_task.id)
        
        # Advance directly to Step 3
        return redirect('execution_page', task_id=new_task.id)

    # GET Request: Render the form with initial context
    return render(request, 'config_form.html', {'mode': mode})


def execution_page_view(request, task_id):
    """Step 3: Real-Time Telemetry Log Display Screen (execution.html)"""
    task = get_object_or_404(AgentTask, id=task_id)
    return render(request, 'execution.html', {'task': task})


# ==========================================
# BRANCH 2: PAST TASKS (TASK CONTROL CENTER)
# ==========================================

def dashboard_view(request):
    """Task Vault Interface (dashboard.html)"""
    tasks = AgentTask.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'tasks': tasks})


def edit_config_view(request, task_id):
    """Task Control Center: Edit an existing configuration state"""
    task = get_object_or_404(AgentTask, id=task_id)
    if request.method == 'POST':
        # Update your config fields here...
        task.save()
        return redirect('dashboard')
    return render(request, 'config_form.html', {'mode': task.mode, 'task': task})


def rerun_task_view(request, task_id):
    """Task Control Center: Re-run an historical pipeline execution"""
    task = get_object_or_404(AgentTask, id=task_id)
    task.status = 'PENDING'
    task.save()
    execute_agent_task(task.id)
    return redirect('execution_page', task_id=task.id)


def duplicate_task_view(request, task_id):
    """Task Control Center: Clone an old configuration profile into a new template run"""
    old_task = get_object_or_404(AgentTask, id=task_id)
    new_task = AgentTask.objects.create(
        mode=old_task.mode,
        status='PENDING',
        config_data=old_task.config_data
    )
    execute_agent_task(new_task.id)
    return redirect('execution_page', task_id=new_task.id)


def delete_task_view(request, task_id):
    """Task Control Center: Delete a record out of the database"""
    task = get_object_or_404(AgentTask, id=task_id)
    task.delete()
    return redirect('dashboard')

from django.http import JsonResponse

def task_status_api(request, task_id):
    """Returns raw execution details for asynchronous terminal updates"""
    task = get_object_or_404(AgentTask, id=task_id)
    return JsonResponse({
        'status': task.status,
        'logs': task.config_data.get('execution_logs', ''), # pulls directly from JSONField state
    })