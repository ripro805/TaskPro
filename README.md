# TaskPro

Role-based task management built with Django. Projects, tasks, assignees, and three
role-specific dashboards (Admin / Manager / Employee) backed by PostgreSQL
(local or Neon).

## Stack

- Python 3.14, Django 5.2
- PostgreSQL (Neon in production)
- python-decouple for env management
- Tailwind / custom CSS for the UI

## Quick start

```powershell
# 1. Clone
git clone https://github.com/ripro805/TaskPro
cd TaskPro

# 2. Create venv and install deps
python -m venv task_env
.\task_env\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Configure env (Neon URL or local Postgres)
Copy-Item .env.example .env
# edit .env and set DATABASE_URL + SECRET_KEY

# 4. Migrate and run
python manage.py migrate
python manage.py runserver
```

## Roles

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `Admin@12345` |
| Manager | `manager` | `Manager@12345` |
| Employee | `employee` | `Employee@12345` |

Reset any of these with `python manage.py changepassword <username>`.

## Database

Set `DATABASE_URL` in `.env`. For Neon:

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST.neon.tech/neondb?sslmode=require
```

If `DATABASE_URL` is empty, Django falls back to a local `db.sqlite3`.

## Project layout

```
core/        # base templates, home, nav
tasks/       # tasks, projects, dashboards
users/       # auth, profiles, admin views
task_management/  # Django project (settings, urls, wsgi)
static/css/  # premium.css, premium-additions.css
media/       # user uploads (gitignored)
```

## Deploy to Render

This repo ships with `render.yaml` (Blueprint) so the entire stack
(DB + web service) can be created from the dashboard.

1. Push your changes to GitHub.
2. In Render, click **New +** → **Blueprint**.
3. Connect the `ripro805/TaskPro` repo and pick the `main` branch.
4. Render reads `render.yaml` and provisions:
   - a free PostgreSQL instance named `taskpro-db`
   - a free web service named `taskpro` running Gunicorn
5. After the first deploy finishes, open **Shell** in the web service
   and create the default accounts:

   ```bash
   python manage.py shell -c "
   from users.models import CustomUser
   for username, pw in [('admin','Admin@12345'),('manager','Manager@12345'),('employee','Employee@12345')]:
       if not CustomUser.objects.filter(username=username).exists():
           CustomUser.objects.create_user(username=username, password=pw)
   "
   ```

Manual setup (without Blueprint):

1. Create a **PostgreSQL** service on Render (free plan works).
2. Create a **Web Service** from this repo:
   - Build command: `./build.sh`
   - Start command: `gunicorn task_management.wsgi --log-file -`
3. Add env vars: `DATABASE_URL` (Internal Database URL from step 1),
   `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=.onrender.com`,
   `SECRET_KEY` (run `python -c "import secrets; print(secrets.token_urlsafe(60))"`),
   `PYTHON_VERSION=3.11.10`.

> Media files (profile pics, task assets) on Render's free tier are
> wiped on every redeploy because the disk is ephemeral. For uploads
> that persist, plug in Cloudinary or a persistent disk.

## License

MIT