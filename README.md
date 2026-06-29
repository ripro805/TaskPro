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

## License

MIT