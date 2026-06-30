"""Vercel entrypoint. Exposes `app` so Vercel's @vercel/python runtime can serve it."""
import os
import sys
from pathlib import Path

# Make the project root importable when Vercel runs from a sub-folder.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Run migrations on cold start; safe no-op after the first run.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_management.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

try:
    from django.core.management import call_command  # noqa: E402

    call_command('migrate', '--noinput', verbosity=0)
except Exception:  # pragma: no cover - never block a request on migration errors
    pass

application = get_wsgi_application()
app = application
