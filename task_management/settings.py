"""Django settings for task_management project."""
import os
from pathlib import Path
from decouple import Config, RepositoryEnv, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# On serverless (Vercel) there is no .env file — secrets come from the
# platform's environment variables.  Guard with an existence check so
# RepositoryEnv never tries to open a missing file.
_env_path = BASE_DIR / ".env"
if _env_path.is_file():
    config = Config(RepositoryEnv(str(_env_path)))
else:
    # No .env → config() will read from os.environ automatically.
    from decouple import AutoConfig
    config = AutoConfig()

# ---- Core security ----
# Fall back to a fixed dev secret so `manage.py check` works in CI before .env
# is provisioned. In production this MUST be overridden via env var.
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-rxff8hi9lx&)j^nzyxw0-w7as8^0nqw+bs#0dx+%_zf70v^r8e',
)

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
# If we are running on Render (it injects RENDER=true into env), force DEBUG off
# regardless of any stale value. Keeps secret-leak errors private.
if os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_URL'):
    DEBUG = False

# Always allow *.onrender.com so accidental missing env var never bricks the
# site. DJANGO_ALLOWED_HOSTS env var still wins when set (CSV list).
_default_hosts = (
    'localhost,127.0.0.1,testserver,.onrender.com'
    if DEBUG
    else 'localhost,127.0.0.1,.onrender.com'
)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default=_default_hosts, cast=Csv())
# Defensive: a mis-configured platform that strips dots from the env value
# shouldn't take the whole site down.
if not any('.onrender.com' in h for h in ALLOWED_HOSTS):
    ALLOWED_HOSTS = list(ALLOWED_HOSTS) + ['.onrender.com']


def _normalize_allowed_hosts():
    """Subdomains strip the leading dot in some env-var parsers — restore it.

    `taskpro-u4b9,onrender,com` should become `taskpro-u4b9.onrender.com`.
    """
    fixed = []
    for host in ALLOWED_HOSTS:
        if ',' in host and not host.startswith('.'):
            parts = host.rsplit(',', 2)
            if len(parts) == 3 and 'onrender' in parts[1]:
                host = '.'.join(parts)
        fixed.append(host.strip())
    ALLOWED_HOSTS[:] = fixed


_normalize_allowed_hosts()

AUTH_USER_MODEL = 'users.CustomUser'

# ---- Apps ----
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tasks",
    "users",
    "core",
]
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

# ---- Middleware ----
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "task_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "task_management.wsgi.application"

# ---- Database (Neon / PostgreSQL via DATABASE_URL, sqlite fallback for dev) ----
import dj_database_url

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ---- Password validation ----
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 4},
    },
]

# ---- I18n ----
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

# ---- Static & media ----
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compress + cache static files for production.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Email ----
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ---- App-specific ----
FRONTEND_URL = config('FRONTEND_URL', default='http://127.0.0.1:8000')
LOGIN_URL = '/users/sign-in/'
LOGIN_REDIRECT_URL = '/tasks/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ---- Production hardening (no-op when DEBUG) ----
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # WhiteNoise will serve /static/ and /media/ when configured.
