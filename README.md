<div align="center">

# ✨ TaskPro

### **Plan, Assign, Deliver — Like a Pro.**

[![Live Demo](https://img.shields.io/badge/LIVE-https://taskpro--u4b9.onrender.com-3b63ff?style=for-the-badge&logo=render&logoColor=white)](https://taskpro-u4b9.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://supabase.com)
[![Render](https://img.shields.io/badge/Hosted_on-Render-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com)

**A premium, role-based task management suite for modern teams.**
Spin up projects, assign work, track progress, and ship faster — with dashboards that look as good as your work.

[🚀 **Launch TaskPro** →](https://taskpro-u4b9.onrender.com)

</div>

---

## 🎨 Premium Design System

TaskPro ships a **hand-crafted, production-grade CSS design system** — no UI framework dependency, no bloat. Every pixel is intentional.

### 🧱 Architecture

| Layer | File | Purpose |
|---|---|---|
| **Foundation** | `premium.css` (113 KB) | Core design system — CSS variables, reset, typography, spacing, layout primitives, component classes, animations, gradients, aurora effects |
| **Extensions** | `premium-additions.css` (32 KB) | Auth pages (split-screen login/signup), profile redesign, footer v2, admin control center, dashboard panels |
| **Utilities** | `output.css` (31 KB) | Tailwind-compiled utility classes for rapid layout tweaks |
| **CDN Runtime** | Tailwind CSS CDN | JIT compiler for custom palette (`brand`, `ink`, `accent`, `violet`, `pink`) — dev convenience only |

### 🎭 Visual Features

- **Aurora Background** — animated gradient mesh (`aurora`, `bg-grid`) behind every page
- **Glassmorphism Cards** — `backdrop-filter: blur()` with translucent borders
- **Brand Palette** — 10-shade `brand` (blue-indigo) + 10-shade `ink` (dark navy) + `accent` (cyan) + `violet` + `pink`
- **Premium Buttons** — `.btn-primary` (gradient + glow shadow), `.btn-ghost` (glass outline), `.btn-xl` / `.btn-sm` sizes
- **Hero Section** — animated mockup window with floating blobs, gradient headline, pulse eyebrow
- **Feature Grid** — 6-card responsive grid with alternating icon colors
- **Pricing Cards** — 3-tier layout with "Most Popular" ribbon, gradient CTA buttons
- **Testimonial Carousel** — star ratings, quote cards, avatar initials
- **FAQ Accordion** — native `<details>` with custom chevron animation
- **CTA Banner** — full-width gradient strip with dual action buttons
- **Footer v2** — 4-column layout, social icons (SVG), newsletter form, status indicator
- **Auth Split-Screen** — left: brand showcase with feature bullets; right: form card
- **Dashboard Panels** — KPI cards, burndown chart placeholder, task list with status dots
- **Smooth Animations** — `anim-fade-up`, `anim-float`, `pulse`, hover scale/translate transitions
- **Responsive** — mobile-first breakpoints, collapsible nav, stacked grids on small screens

### 🖌️ CSS Variable Map

```css
:root {
  /* Brand — primary blue-indigo */
  --brand-50 … --brand-900
  /* Ink — dark navy (backgrounds, text) */
  --ink-50 … --ink-900
  /* Accent — cyan */
  --accent-400 … --accent-600
  /* Semantic */
  --success  --warning  --danger  --info
  /* Radius */
  --radius-sm: 8px;  --radius: 14px;  --radius-lg: 20px;  --radius-xl: 28px;
  /* Shadows */
  --shadow-glow: 0 18px 40px -12px rgba(59,99,255,.45);
}
```

---

## 🏗️ Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · Django 5.2 · Gunicorn 23 |
| **Database** | PostgreSQL via Supabase (transaction pooler, port 6543, sslmode=require) |
| **Auth** | Django custom user model (`CustomUser`) · role-based access (Admin / Manager / Employee) |
| **Static Files** | WhiteNoise 6.7 (compressed, finder-based serving) · 3-layer CSS design system |
| **Env Management** | python-decouple 3.8 (AutoConfig with `.env` fallback) |
| **Email** | Gmail SMTP (App Password) for password reset & notifications |
| **Hosting** | Render (free tier, Blueprint-based deploy) |
| **CI/CD** | Git push → Render auto-build (`build.sh`) → zero-downtime deploy |

---

## 🚀 Live Demo

👉 **[https://taskpro-u4b9.onrender.com](https://taskpro-u4b9.onrender.com)**

| Page | URL | Description |
|---|---|---|
| Landing | `/` | Hero, features, pricing, testimonials, FAQ, CTA, footer |
| Sign In | `/users/sign-in/` | Split-screen auth with brand showcase |
| Sign Up | `/users/sign-up/` | Registration with role selection |
| Admin Dashboard | `/tasks/admin-dashboard/` | Full control — users, tasks, projects |
| Manager Dashboard | `/tasks/manager-dashboard/` | Assign & track team work |
| Employee Dashboard | `/tasks/employee-dashboard/` | Personal task list & status updates |

> ⏱ Free tier cold start: first request after idle may take ~30 s. Subsequent requests are instant.

## ⚡ Quick Start

```powershell
# 1. Clone
git clone https://github.com/ripro805/TaskPro
cd TaskPro

# 2. Virtual env + deps
python -m venv task_env
.\task_env\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Configure env
Copy-Item .env.example .env
# edit .env → set DATABASE_URL + SECRET_KEY + EMAIL_*

# 4. Migrate + seed demo users + run
python manage.py migrate
python manage.py seed_users
python manage.py runserver
```

Open **http://127.0.0.1:8000** → enjoy the aurora.

### 👥 Default Roles (Seed Users)

| Role | Username | Password | Capabilities |
|---|---|---|---|
| 🛡️ **Admin** | `admin` | `Admin@12345` | Full control — manage users, projects, every task |
| 📋 **Manager** | `manager` | `Manager@12345` | Create projects, assign tasks to employees, track velocity |
| 👨‍💻 **Employee** | `employee` | `Employee@12345` | View assigned tasks, update status, comment |

> ⚠️ Change all demo passwords before going live. `python manage.py changepassword <username>` resets any of them.

---

## 🗄️ Database

Production uses **Supabase PostgreSQL** (transaction-mode pooler, port `6543`, `sslmode=require`) via `dj-database-url`. Local dev defaults to SQLite for zero-config onboarding.

```env
# .env
DATABASE_URL=postgresql://USER:PASSWORD@HOST.supabase.co:6543/postgres?sslmode=require
```

If `DATABASE_URL` is empty, Django falls back to a local `db.sqlite3`.

---

## 📁 Project Layout

```
task_management/
├── core/                # Base templates, landing page, nav
├── tasks/               # Tasks, projects, role-based dashboards
│   ├── templates/       # show_tasks, task_detail, task_form, dashboard/
│   └── management/
│       └── commands/
│           └── seed_users.py   # Idempotent demo user seeder
├── users/               # Custom user, auth views, profiles, admin
├── task_management/     # Django project (settings, urls, wsgi, asgi)
├── static/css/
│   ├── premium.css              # ⭐ Design system foundation (113 KB)
│   ├── premium-additions.css    # ⭐ Auth + Footer + Profile (32 KB)
│   └── output.css               # Tailwind utilities (31 KB)
├── media/               # User uploads (gitignored — profile pics, task assets)
├── render.yaml          # Render Blueprint — DB + web service
├── build.sh             # Build script — migrate + collectstatic
├── runtime.txt          # Python 3.11.10
└── requirements.txt     # Pinned dependencies
```

---

## 🚢 Deploy to Render

This repo ships with **`render.yaml`** (Blueprint) so the entire stack (DB + web service) is provisioned in one click.

### Option A — Blueprint (Recommended)

1. Push changes to GitHub.
2. In Render → **New +** → **Blueprint**.
3. Connect the `ripro805/TaskPro` repo → pick `main`.
4. Render reads `render.yaml` and provisions:
   - A PostgreSQL instance named `taskpro-db`
   - A web service named `taskpro` running Gunicorn
5. After first deploy, run the seeder (one-time):
   ```bash
   python manage.py seed_users
   ```
   Or use `Render Shell` and the inline shell snippet documented in the Blueprint.

### Option B — Manual

1. Create a **PostgreSQL** service on Render (free plan works).
2. Create a **Web Service** from this repo:
   - **Build command:** `./build.sh`
   - **Start command:** `gunicorn task_management.wsgi --log-file -`
3. Set env vars:
   - `DATABASE_URL` → Internal Database URL from step 1
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=.onrender.com`
   - `SECRET_KEY` → `python -c "import secrets; print(secrets.token_urlsafe(60))"`
   - `PYTHON_VERSION=3.11.10`
   - `EMAIL_HOST_USER` + `EMAIL_HOST_PASSWORD` (Gmail App Password)

> 📝 Media files (profile pics, task assets) on Render's free tier are wiped on every redeploy (ephemeral disk). For persistent uploads, plug in Cloudinary or a Render persistent disk.

---

## 🧩 Why TaskPro Stands Out

| ✨ | Feature |
|---|---|
| 🎨 | **Premium design system** — 176 KB of hand-crafted CSS, zero UI framework lock-in |
| 🔐 | **Role-based access** — Admin / Manager / Employee with isolated dashboards |
| 🗄️ | **Production PostgreSQL** — Supabase pooler, SSL-enforced, migrations auto-applied |
| 📦 | **One-click deploy** — Render Blueprint provisions everything |
| 🌱 | **Demo seeder** — `seed_users` command for instant exploration |
| 📱 | **Fully responsive** — mobile, tablet, desktop |
| 🆓 | **Free tier friendly** — runs on Render's free PostgreSQL + free web service |
| 🔄 | **CI/CD built-in** — `git push` → auto-deploy |

---

## 📄 License

MIT — free to use, modify, and ship.

---

<div align="center">

**Built with ❤️ by [ripro805](https://github.com/ripro805)**

[🚀 Launch Live Demo →](https://taskpro-u4b9.onrender.com) · [⭐ Star on GitHub](https://github.com/ripro805/TaskPro) · [🐛 Report Bug](https://github.com/ripro805/TaskPro/issues)

</div>