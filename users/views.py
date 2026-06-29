from django.views.generic import TemplateView
# Base profile view using TemplateView

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from users.forms import RegisterForm, CustomizeRegisterForm,LoginForm, AssignRoleForm,CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm, EditProfileForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login as auth_login , logout
from django.shortcuts import redirect
from django.contrib import messages
from users.forms import StyledAuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.

# Class-based logout view
  # Optional: customize logout page

#test for user
def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_superuser

def sign_up(request):
    if request.method == 'GET':
        form = CustomizeRegisterForm()
    elif request.method == 'POST':
        form = CustomizeRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # Activation email will be sent automatically by signal
            messages.success(request, "A confirmation email has been sent to your email address. Please activate your account.")
            return redirect('sign_in')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    return render(request, 'registration/register.html', {'form': form})


def sign_in(request):
    form=LoginForm()
    if request.method=='POST':
        form=LoginForm(request=request,data=request.POST)
        if form.is_valid():
           user=form.get_user()
           auth_login(request, user)
           return redirect('home')
    return render(request, 'registration/login.html', {'form': form})
           
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    def get_success_url(self):
        next_url=self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()
class CustomLogoutView(LogoutView):
    next_page = "home"  # Redirect to home after logout

# Password change views
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = '/users/password_change/done/'

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

# Password change views
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    form_class = CustomPasswordChangeForm
    success_url = '/users/password_change/done/'

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

# Password reset views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    html_email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/users/password_reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = '/users/password_reset/complete/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
@login_required           
def sign_out(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


def activate_account(request, uidb64, token):
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link.")
        return redirect('sign_in')

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully. You can now log in.")
        return redirect('sign_in')
    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect('sign_in')


@user_passes_test(is_admin,login_url='sign_in')    
def admin_dashboard(request):
    User = get_user_model()
    users = User.objects.only('id', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'date_joined').prefetch_related(
        Prefetch('groups', queryset=Group.objects.only('id', 'name'))
    ).order_by('-date_joined')

    # Use prefetched data - no additional queries
    for user in users:
        groups = list(user.groups.all())  # Uses prefetched cache
        user.group_name = groups[0].name if groups else "No Group Assigned"

    # KPI aggregates
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    inactive_users = total_users - active_users
    recent_users = User.objects.order_by('-date_joined')[:5]
    active_rate = int(round((active_users / total_users) * 100)) if total_users else 0

    groups = Group.objects.all().order_by('name')
    total_groups = groups.count()

    # ---- Task metrics for the rich admin template ----
    from tasks.models import Task, Project
    from django.db.models import Q
    from django.utils import timezone as _tz

    task_counts = {
        'total':       Task.objects.count(),
        'pending':     Task.objects.filter(status='PENDING').count(),
        'in_progress': Task.objects.filter(status='IN_PROGRESS').count(),
        'completed':   Task.objects.filter(status='COMPLETED').count(),
    }
    task_completion_rate = int(round((task_counts['completed'] / task_counts['total']) * 100)) if task_counts['total'] else 0
    overdue_tasks_count = Task.objects.filter(due_date__lt=_tz.now().date()).exclude(status='COMPLETED').count()
    project_count = Project.objects.count()

    # Per-group membership counts (sorted by member count desc)
    group_distribution = (
        Group.objects
        .annotate(num_members=Count('user', distinct=True))
        .order_by('-num_members', 'name')
    )

    # System-wide recent tasks preview
    recent_tasks = (
        Task.objects
        .select_related('detail', 'project')
        .prefetch_related('assigned_to')
        .order_by('-created_at')[:8]
    )

    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'staff_users': staff_users,
        'total_groups': total_groups,
        'recent_users': recent_users,
        'groups': groups,
        'active_rate': active_rate,
        'task_counts': task_counts,
        'task_completion_rate': task_completion_rate,
        'overdue_tasks_count': overdue_tasks_count,
        'project_count': project_count,
        'group_distribution': group_distribution,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@user_passes_test(is_admin,login_url='no_permission')    
def assign_role(request, user_id):
    User = get_user_model()
    user = User.objects.prefetch_related('groups').get(id=user_id)
    form = AssignRoleForm()
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            user.groups.clear()  # Clear existing roles
            user.groups.add(role)  # Assign new role
            user.save()
            messages.success(request, f"Role '{role.name}' has been assigned to {user.username}.")
            return redirect('admin_dashboard')
    
    return render(request, 'admin/assign_role.html', {'form': form, 'user': user})
@user_passes_test(is_admin,login_url='no_permission')    
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group= form.save()
            messages.success(request, f"Group '{group.name}' created successfully.")
            return redirect('create_group')
    return render(request, 'admin/create_group.html', {'form': form})
@user_passes_test(is_admin,login_url='no_permission')    
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Profile fields are on the custom user model
        context['user'] = user
        context['profile'] = {
            'bio': getattr(user, 'bio', ''),
            'profile_picture': getattr(user, 'profile_picture', None),
        }
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name() or user.username
        # Add user roles (group names)
        try:
            context['roles'] = list(user.groups.values_list('name', flat=True))
        except Exception:
            context['roles'] = []
        return context

from users.forms import EditProfileForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class EditProfileView(TemplateView):
    template_name = 'accounts/edit_profile.html'

    def get(self, request, *args, **kwargs):
        form = EditProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})