from django.shortcuts import render, redirect
from django.urls import reverse


def home(request):
    """Landing page with hero, features and role CTAs."""
    context = {
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'home.html', context)


def no_permission(request):
    """Branded 403 page. If anonymous, bounce to sign-in with `?next=`."""
    if not request.user.is_authenticated:
        login_url = reverse('sign_in')
        next_url = request.get_full_path()
        return redirect(f'{login_url}?next={next_url}')
    return render(request, 'no_permission.html')