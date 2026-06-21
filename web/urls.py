from django.contrib import admin
from django.urls import path
from web.views import dashboard_view, dispatch_task_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('dispatch/', dispatch_task_view, name='dispatch_task'),
]