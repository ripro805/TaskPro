from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.db.models import Q, Count
from django.contrib import messages
from .forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Employee, Task, TaskDetail, Project
from datetime import date
from django.utils import timezone as django_timezone

#Class based view for reuse example
class GreetingView(View):
    greetings = "Hello, welcome to the Task Management System!"
    def get(self, request):
        return HttpResponse(self.greetings)

class HiGreetingView(GreetingView):
    greetings = "Hi there! This is a personalized greeting from HiGreetingView."
# Create your views here.

def is_manager(user):
    return user.groups.filter(name='Manager').exists()
def is_employee(user):
    return user.groups.filter(name='Employee').exists()
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


class ManagerDashboardView(LoginRequiredMixin, View):
    login_url = reverse_lazy("sign_in")
    redirect_field_name = "next"

    @method_decorator(user_passes_test(is_manager, login_url="sign_in"), name="dispatch")
    def get(self, request):
        context = self.get_context_data()
        return render(request, "dashboard/manager_dashboard.html", context)

    def _scope_qs(self):
        """Base queryset matching the manager role."""
        user = self.request.user
        if is_admin(user) or is_manager(user):
            return (
                Task.objects
                .select_related("detail", "project")
                .prefetch_related("assigned_to")
                .order_by("-created_at")
            )
        return (
            Task.objects
            .filter(assigned_to=user)
            .select_related("detail", "project")
            .prefetch_related("assigned_to")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = {}
        user = self.request.user

        scope = self._scope_qs()

        # KPI counts against the full manager scope
        task_counts = {
            "total":       scope.count(),
            "pending":     scope.filter(status="PENDING").count(),
            "in_progress": scope.filter(status="IN_PROGRESS").count(),
            "completed":   scope.filter(status="COMPLETED").count(),
        }
        completion_rate = int(round((task_counts["completed"] / task_counts["total"]) * 100)) if task_counts["total"] else 0

        today = django_timezone.now().date()

        # Overdue tasks (not yet completed, past due date)
        overdue_tasks = list(
            scope.filter(status__in=["PENDING", "IN_PROGRESS"])
                 .filter(due_date__lt=today)
                 .select_related("detail", "project")
                 .prefetch_related("assigned_to")
                 .order_by("due_date")[:6]
        )

        # Top contributors — users annotated by completed-task counts
        # Task.assigned_to is an m2m to AUTH_USER_MODEL with related_name="tasks",
        # so the reverse from CustomUser is `tasks` (not `task`).
        from django.contrib.auth import get_user_model
        User = get_user_model()
        top_contributors = list(
            User.objects
            .annotate(
                done_count=Count("tasks", filter=Q(tasks__status="COMPLETED"), distinct=True),
                inprog_count=Count("tasks", filter=Q(tasks__status="IN_PROGRESS"), distinct=True),
            )
            .filter(done_count__gt=0)
            .order_by("-done_count", "-inprog_count")[:6]
        )

        # Projects the manager actually has tasks in (annotated for KPIs)
        if is_admin(user) or is_manager(user):
            projects = (
                Project.objects
                .annotate(
                    num_task=Count("task", distinct=True),
                    num_pending=Count("task", filter=Q(task__status="PENDING"), distinct=True),
                    num_inprogress=Count("task", filter=Q(task__status="IN_PROGRESS"), distinct=True),
                    num_completed=Count("task", filter=Q(task__status="COMPLETED"), distinct=True),
                )
                .order_by("-num_task")
            )
            context_message = "All Tasks (Admin/Manager View)"
            role_label = "Admin" if user.is_superuser else ("Admin" if is_admin(user) else "Manager")
        else:
            projects = (
                Project.objects
                .filter(task__in=scope)
                .annotate(
                    num_task=Count("task", distinct=True),
                    num_pending=Count("task", filter=Q(task__status="PENDING"), distinct=True),
                    num_inprogress=Count("task", filter=Q(task__status="IN_PROGRESS"), distinct=True),
                    num_completed=Count("task", filter=Q(task__status="COMPLETED"), distinct=True),
                )
                .order_by("-num_task")
                .distinct()
            )
            context_message = "My Assigned Tasks"
            role_label = "Employee"

        # Per-project tasks (heatmap-friendly dict shape)
        projects_with_tasks = []
        for project in projects[:8]:
            proj_tasks = (
                scope.filter(project=project)
                .select_related("detail", "project")
                .prefetch_related("assigned_to")
                .order_by("-created_at")[:6]
            )
            projects_with_tasks.append({
                "project": project,
                "tasks": proj_tasks,
                "total": project.num_task,
                "count": project.num_task,
                "done": project.num_completed,
                "inprogress": project.num_inprogress,
                "pending": project.num_pending,
            })

        projects_count = projects.count()
        team_size = Employee.objects.count()

        # Tasks list shown in the recent-activity table
        status_filter = self.request.GET.get("status", "").upper()
        valid_statuses = {choice[0] for choice in Task.STATUS_CHOICES}
        if status_filter in valid_statuses:
            tasks_list = scope.filter(status=status_filter).select_related("detail", "project").prefetch_related("assigned_to")
        else:
            tasks_list = scope.select_related("detail", "project").prefetch_related("assigned_to")
            status_filter = ""

        context.update({
            "tasks": tasks_list,
            "projects": projects,
            "projects_with_tasks": projects_with_tasks,
            "projects_count": projects_count,
            "team_size": team_size,
            "overdue_tasks": overdue_tasks,
            "top_contributors": top_contributors,
            "context_message": context_message,
            "task_counts": task_counts,
            "completion_rate": completion_rate,
            "role_label": role_label,
            "status_filter": status_filter,
        })
        return context

class EmployeeDashboardView(LoginRequiredMixin, View):
    """
    Premium dashboard for employees — uses the full show_tasks-style layout
    (hero strip, KPI cards, filter pills, tasks table, project group section)
    so the dashboard surface is rich and matches the task list page in design.
    """
    login_url = reverse_lazy('sign_in')
    redirect_field_name = 'next'
    @method_decorator(user_passes_test(is_employee, login_url='sign_in'), name='dispatch')
    def get(self, request):
        context = self.get_context_data()
        return render(request, 'dashboard/employee_dashboard.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        user = self.request.user

        # Base queryset: only tasks assigned to this employee
        scope = (
            Task.objects
            .filter(assigned_to=user)
            .select_related('detail', 'project')
            .prefetch_related('assigned_to')
        )

        # Status filter from querystring
        status_filter = self.request.GET.get('status', '').upper()
        valid_statuses = {choice[0] for choice in Task.STATUS_CHOICES}
        if status_filter in valid_statuses:
            tasks = scope.filter(status=status_filter)
        else:
            tasks = scope.order_by('-created_at')
            status_filter = ''

        # KPI counts (against the full scope, not the filter)
        task_counts = {
            'total':       scope.count(),
            'pending':     scope.filter(status='PENDING').count(),
            'in_progress': scope.filter(status='IN_PROGRESS').count(),
            'completed':   scope.filter(status='COMPLETED').count(),
        }

        # Projects the employee actually has tasks in
        projects = (
            Project.objects
            .filter(task__in=scope)
            .annotate(
                num_task=Count('task', distinct=True),
                num_pending=Count('task', filter=Q(task__status='PENDING'), distinct=True),
                num_inprogress=Count('task', filter=Q(task__status='IN_PROGRESS'), distinct=True),
                num_completed=Count('task', filter=Q(task__status='COMPLETED'), distinct=True),
            )
            .order_by('-num_task')
            .distinct()
        )

        # Per-project tasks (first 5 each, for the project group section)
        projects_with_tasks = []
        for project in projects[:6]:
            proj_tasks = scope.filter(project=project).order_by('-created_at')[:5]
            projects_with_tasks.append({
                'project': project,
                'tasks': proj_tasks,
                'total': project.num_task,
            })

        context.update({
            'tasks': tasks,
            'my_tasks': scope,                  # kept for any legacy refs
            'task_counts': task_counts,
            'projects': projects,
            'projects_with_tasks': projects_with_tasks,
            'context_message': 'My Assigned Tasks',
            'role_label': 'Employee',
            'status_filter': status_filter,
            'current_user': user,
        })
        return context

# Class-based view for test
class TestView(View):
    def get(self, request):
        names = ["Mahmud", "Ahamed", "John", "Mr. X"]
        count = len(names)
        context = {
            "names": names,
            "age": 23,
            "count": count
        }
        return render(request, 'test.html', context)



class CreateTaskView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    login_url = 'sign_in'
    redirect_field_name = 'next'
    permission_required = 'tasks.add_task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        context['task_detail_form'] = TaskDetailModelForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        task_form = self.get_form()
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task created successfully!')
            return redirect('create-task')
        return self.render_to_response(self.get_context_data(form=task_form, task_detail_form=task_detail_form))



class UpdateTaskView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    login_url = 'sign_in'
    redirect_field_name = 'next'
    permission_required = 'tasks.change_task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        try:
            task_detail = task.detail
            task_detail_form = TaskDetailModelForm(instance=task_detail)
        except TaskDetail.DoesNotExist:
            task_detail_form = TaskDetailModelForm()
        context['task_form'] = self.get_form()
        context['task_detail_form'] = task_detail_form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = self.get_form()
        try:
            task_detail = self.object.detail
            task_detail_form = TaskDetailModelForm(request.POST, request.FILES, instance=task_detail)
        except TaskDetail.DoesNotExist:
            task_detail_form = TaskDetailModelForm(request.POST, request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('manager_dashboard')
        return self.render_to_response(self.get_context_data(form=task_form, task_detail_form=task_detail_form))


class ViewTasksView(LoginRequiredMixin, ListView):
    """
    Premium list view for tasks.

    Permission model:
      - Admin / Manager: see every task (full visibility).
      - Employee: see only tasks assigned to them.

    We intentionally avoid Django's `PermissionRequiredMixin` here because
    Employees usually don't carry the `tasks.view_task` model permission — 
    they only see what's been assigned to them. Group membership is the 
    correct gate.
    """
    model = Task
    template_name = 'show_tasks.html'
    context_object_name = 'tasks'
    login_url = 'sign_in'
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (is_admin(request.user) or is_manager(request.user) or is_employee(request.user)):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if is_admin(user) or is_manager(user):
            return Task.objects.select_related('detail', 'project').prefetch_related('assigned_to').order_by('-created_at')
        # Employee — only assigned tasks
        return (
            Task.objects
            .filter(assigned_to=user)
            .select_related('detail', 'project')
            .prefetch_related('assigned_to')
            .order_by('-created_at')
        )

    def _scope_qs(self):
        """Base queryset matching the role, used for stats & projects."""
        user = self.request.user
        if is_admin(user) or is_manager(user):
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        scope = self._scope_qs()

        # Optional project filter
        selected_project = None
        project_id = self.request.GET.get('project')
        if project_id and project_id.isdigit():
            proj_qs = Project.objects.filter(id=int(project_id))
            if is_admin(user) or is_manager(user):
                selected_project = proj_qs.first()
            else:
                selected_project = proj_qs.filter(task__in=scope).distinct().first()
            if selected_project:
                scope = scope.filter(project=selected_project)

        # Optional search query (matches title or description, case-insensitive)
        search_query = (self.request.GET.get('q') or '').strip()
        if search_query:
            scope = scope.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

        # Status filter (from querystring)
        status_filter = self.request.GET.get('status', '').upper()
        valid_statuses = {choice[0] for choice in Task.STATUS_CHOICES}
        if status_filter in valid_statuses:
            filtered_tasks = scope.filter(status=status_filter).select_related('detail', 'project').prefetch_related('assigned_to')
        else:
            filtered_tasks = context['tasks']
            status_filter = ''

        # KPI counts (always computed against the user's full scope, not the filter)
        task_counts = {
            'total':     scope.count(),
            'pending':   scope.filter(status='PENDING').count(),
            'in_progress': scope.filter(status='IN_PROGRESS').count(),
            'completed': scope.filter(status='COMPLETED').count(),
        }

        # Projects the user actually has access to
        if is_admin(user) or is_manager(user):
            projects = (
                Project.objects
                .annotate(
                    num_task=Count('task', distinct=True),
                    num_pending=Count('task', filter=Q(task__status='PENDING'), distinct=True),
                    num_inprogress=Count('task', filter=Q(task__status='IN_PROGRESS'), distinct=True),
                    num_completed=Count('task', filter=Q(task__status='COMPLETED'), distinct=True),
                )
                .order_by('-num_task')
            )
            context_message = "All Tasks (Admin/Manager View)"
            role_label = 'Admin' if user.is_superuser else ('Admin' if is_admin(user) else 'Manager')
        else:
            projects = (
                Project.objects
                .filter(task__in=scope)
                .annotate(
                    num_task=Count('task', distinct=True),
                    num_pending=Count('task', filter=Q(task__status='PENDING'), distinct=True),
                    num_inprogress=Count('task', filter=Q(task__status='IN_PROGRESS'), distinct=True),
                    num_completed=Count('task', filter=Q(task__status='COMPLETED'), distinct=True),
                )
                .order_by('-num_task')
                .distinct()
            )
            context_message = "My Assigned Tasks"
            role_label = 'Employee'

        # Per-project tasks (only first 5 each, for the project group section)
        projects_with_tasks = []
        for project in projects[:6]:
            proj_tasks = filtered_tasks.filter(project=project) if status_filter else scope.filter(project=project).select_related('detail', 'project').prefetch_related('assigned_to')
            projects_with_tasks.append({
                'project': project,
                'tasks': proj_tasks.order_by('-created_at')[:5],
                'total': project.num_task,
            })

        context.update({
            'projects': projects,
            'projects_with_tasks': projects_with_tasks,
            'context_message': context_message,
            'task_counts': task_counts,
            'role_label': role_label,
            'status_filter': status_filter,
            'tasks': filtered_tasks,
            'selected_project': selected_project,
            'search_query': search_query,
        })
        return context



class ViewTaskDetailView(LoginRequiredMixin, DetailView):
    """
    Premium task detail page.

    Bug fix history
    --------------- 
    Previously this view used ``PermissionRequiredMixin`` with 
    ``permission_required = 'tasks.view_task'``.  Employees do not have 
    ``view_task`` permission, so the page returned ``403 Forbidden`` for the 
    primary user role that needs it most.  Viewing is non-destructive, so we 
    now only require login and gate the *write* path (status update) on 
    ``tasks.change_task`` inside ``post()``.
    """
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    login_url = 'sign_in'
    redirect_field_name = 'next'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return (
            Task.objects
            .select_related('detail', 'project')
            .prefetch_related('assigned_to__groups')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        team_members = []
        for user in task.assigned_to.all():
            groups = user.groups.all()
            role = groups[0].name if groups else 'Team Member'
            team_members.append({
                'user': user,
                'role': role,
                'groups': [g.name for g in groups],
            })
        context['team_members'] = team_members
        context['status_choices'] = Task.STATUS_CHOICES
        # Computed convenience values for the premium template
        if task.detail and task.detail.priority == 'H':
            context['progress'] = 100 if task.is_completed else 65
        elif task.detail and task.detail.priority == 'M':
            context['progress'] = 100 if task.is_completed else 50
        else:
            context['progress'] = 100 if task.is_completed else 30
        if task.due_date and not task.is_completed and task.due_date < django_timezone.now().date():
            context['is_overdue'] = True
        else:
            context['is_overdue'] = False
        context['can_change'] = self.request.user.has_perm('tasks.change_task')
        context['can_delete'] = self.request.user.has_perm('tasks.delete_task')
        return context

    def post(self, request, id):
        task = Task.objects.select_related('detail', 'project').prefetch_related('assigned_to__groups').get(id=id)
        if request.user.has_perm('tasks.change_task') and 'task_status' in request.POST:
            new_status = request.POST.get('task_status')
            valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
            if new_status in valid_statuses:
                task.status = new_status
                task.is_completed = (new_status == 'COMPLETED')
                task.save()
                messages.success(request, f'Task status updated to {task.get_status_display()}!')
            return redirect('view_task_detail', id=id)
        else:
            messages.error(request, 'You do not have permission to change task status.')
        # Re-render the detail page with the same context as GET
        team_members = []
        for user in task.assigned_to.all():
            groups = user.groups.all()
            role = groups[0].name if groups else 'Team Member'
            team_members.append({
                'user': user,
                'role': role,
                'groups': [g.name for g in groups],
            })
        context = {
            'task': task,
            'team_members': team_members,
            'status_choices': Task.STATUS_CHOICES,
        }
        return render(request, 'task_detail.html', context)

class DeleteTaskView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    template_name = 'confirm_delete.html'
    context_object_name = 'task'
    login_url = 'sign_in'
    redirect_field_name = 'next'
    permission_required = 'tasks.delete_task'
    pk_url_kwarg = 'id'
    success_url = '/tasks/manager-dashboard/'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)
