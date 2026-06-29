from django import template
from datetime import datetime
from django.utils import timezone
register = template.Library()

# Example filter: capitalize first letter
@register.filter
def capitalize_first(value):
    if isinstance(value, str) and value:
        return value[0].upper() + value[1:]
    return value

@register.filter
def format_date(value):
    if value:
        today = datetime.now().date()
        if value.date() == today:
            return f"Today at {value.strftime('%I:%M %p')}"
        return value.strftime('%B %d, %Y')
    return "N/A"
@register.filter(name="in_group")
def in_group(user, group_name):
    """True if user is in the named group. Also true if user.is_superuser and group_name is 'Admin'."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if group_name == "Admin" and getattr(user, "is_superuser", False):
        return True
    try:
        return user.groups.filter(name__iexact=group_name).exists()
    except Exception:
        return False

@register.filter(name="primary_role")
def primary_role(user):
    """Return the highest-priority role label for the user: Admin/Manager/Employee/Member."""
    if not user or not getattr(user, "is_authenticated", False):
        return "Guest"
    if getattr(user, "is_superuser", False):
        return "Admin"
    groups = {g.name.lower() for g in user.groups.all()}
    if "admin" in groups:
        return "Admin"
    if "manager" in groups:
        return "Manager"
    if "employee" in groups:
        return "Employee"
    return "Member"