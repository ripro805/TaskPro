"""Vercel entrypoint.

Exposes `app` so the @vercel/python runtime can serve Django via WSGI.

Migrations are intentionally NOT run from here. Vercel functions are
stateless and cold-start frequently; running `migrate` inside a request
handler opens a DB connection at every cold start, slows responses, and
masks real errors. Run migrations once via the Django shell or a build
hook before going live.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_management.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
app = application
