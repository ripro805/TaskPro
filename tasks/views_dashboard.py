from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def dashboard_redirect(request):
    """Route authenticated users to the dashboard for their primary role."""
    user = request.user
    if user.groups.filter(name='Admin').exists() or user.is_superuser:
        return redirect('admin_dashboard')
    if user.groups.filter(name='Manager').exists():
        return redirect('manager_dashboard')
    if user.groups.filter(name='Employee').exists():
        return redirect('employee_dashboard')
    return redirect('no_permission')
