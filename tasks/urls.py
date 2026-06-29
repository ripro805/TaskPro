from django.urls import path
from tasks.views import (
    ManagerDashboardView, EmployeeDashboardView, TestView, CreateTaskView, ViewTasksView, ViewTaskDetailView, UpdateTaskView, DeleteTaskView, GreetingView, HiGreetingView
)
from tasks.views_dashboard import dashboard_redirect

urlpatterns = [
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('manager-dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('employee-dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    path('test/', TestView.as_view()),
    path('create-task/', CreateTaskView.as_view(), name='create-task'),
    path('view-tasks/', ViewTasksView.as_view(), name='view_tasks'),
    path('view-tasks/<int:id>/details/', ViewTaskDetailView.as_view(), name='view_task_detail'),
    path('update-task/<int:id>/', UpdateTaskView.as_view(), name='update-task'),
    path('delete-task/<int:id>/', DeleteTaskView.as_view(), name='delete-task'),
    path('greetings/', HiGreetingView.as_view(), name='greetings'),
]