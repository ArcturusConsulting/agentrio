from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import AgentTask

def dashboard_view(request):
    # Fetch all tasks from SQLite, newest first, to display in the matrix
    tasks = AgentTask.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'tasks': tasks})

@require_POST
def dispatch_task_view(request):
    mode = request.POST.get('mode')
    provider = request.POST.get('provider')
    model_string = request.POST.get('model')
    prompt_input = request.POST.get('prompt_input')

    # If the user leaves the model string blank, we can establish an empty 
    # string or let our downstream module fallback to a default model.
    if not model_string:
        model_string = ""

    # Package the incoming form fields into our decoupled ACL JSON block
    packed_config = {
        "provider": provider,
        "model": model_string.strip(),
        "prompt_input": prompt_input.strip()
    }

    # Save the task to SQLite as PENDING. This instantly prints it to the UI.
    new_task = AgentTask.objects.create(
        mode=mode,
        status='PENDING',
        config_data=packed_config
    )

    # TODO: In the next phase, we will trigger our modules.task_runner here!

    return redirect('dashboard')