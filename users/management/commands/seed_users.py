"""Seed the three demo accounts (Admin / Manager / Employee).

Idempotent: re-running is safe; existing usernames are skipped.
Use from Render's free tier via the "Run Command" feature:

    python manage.py seed_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEMO_ACCOUNTS = [
    ("admin",    "Admin@12345"),
    ("manager",  "Manager@12345"),
    ("employee", "Employee@12345"),
]


class Command(BaseCommand):
    help = "Create the Admin / Manager / Employee demo accounts if they don't exist."

    def handle(self, *args, **options):
        created = 0
        for username, password in DEMO_ACCOUNTS:
            user, was_created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_active = True
            user.is_staff = (username == "admin")
            user.is_superuser = (username == "admin")
            user.save()
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  + created {username}"))
            else:
                self.stdout.write(f"  = updated  {username}")
        self.stdout.write(self.style.SUCCESS(f"Done. {created} new, {len(DEMO_ACCOUNTS) - created} updated."))
