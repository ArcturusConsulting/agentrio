# agentrio/web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Wizard Pattern
    path('', views.select_mode_view, name='select_mode'),
    path('configure/', views.config_form_view, name='config_form'),
    path('execution/<int:task_id>/', views.execution_page_view, name='execution_page'),
    
    # Dashboard Pattern
    path('tasks/', views.dashboard_view, name='dashboard'),
    path('tasks/<int:task_id>/edit/', views.edit_config_view, name='edit_config'),
    path('tasks/<int:task_id>/rerun/', views.rerun_task_view, name='rerun_task'),
    path('tasks/<int:task_id>/duplicate/', views.duplicate_task_view, name='duplicate_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task_view, name='delete_task'),
    path('execution/<int:task_id>/status/', views.task_status_api, name='task_status_api'),
]