# Md Alamin Sk — Personal Portfolio

A responsive personal developer portfolio built with Flask, SQLAlchemy, and vanilla HTML, CSS, and JavaScript. It presents my work and skills, stores projects in a database, and includes a private dashboard for managing portfolio content.

## Features

- Responsive portfolio with accessible mobile navigation and reduced-motion support
- Flask backend with SQLite for local development and PostgreSQL for deployment
- Private admin dashboard with secure, hashed-password authentication and CSRF protection
- Project management: add, edit, publish, feature, reorder, and delete projects
- Profile settings for name, role, introduction, social links, and profile picture upload
- Project thumbnail uploads, GitHub links, live demos, technology tags, categories, and details
- Validated contact form; messages are stored for review in the admin dashboard
- Project filtering, scroll reveals, active section navigation, progress indicator, and back-to-top control
- SEO title, description, Open Graph metadata, and favicon

## Tech stack

Python · Flask · Flask-SQLAlchemy · SQLAlchemy · HTML · CSS · JavaScript · SQLite/PostgreSQL · Git/GitHub

## Screenshots

Add screenshots to `screenshots/` and link them here. No screenshots are included yet.

## Local installation

From a terminal:

```powershell
git clone https://github.com/Ace0th/personal-portfolio.git
cd personal-portfolio
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.

Edit `.env` and set a long random `SECRET_KEY`, your `ADMIN_EMAIL`, and a private `ADMIN_PASSWORD` with at least 12 characters. The example values are placeholders. Keep `.env` private; it is ignored by Git.

Create the database tables and the initial administrator, then start the local server:

```powershell
flask --app run.py create-admin
flask --app run.py run
```

The app creates tables on first startup and seeds the Employee Management System project when the projects table is empty. Open <http://127.0.0.1:5000> for the portfolio and <http://127.0.0.1:5000/admin/login> for admin login. There is no public admin signup. `create-admin` refuses to create another account once an admin exists.

## Deployment on Render

The included [`render.yaml`](render.yaml) configures a Flask web service, HTTPS-only session cookies, a generated secret key, and a persistent disk for uploaded profile/project images. The persistent disk requires a paid Render web service. Create a Render PostgreSQL database and connect its internal connection URL as `DATABASE_URL`; the database also needs a persistent production plan. Check Render's current pricing before provisioning resources.

1. Push this repository to GitHub and create a Render Blueprint from it.
2. Create a Render PostgreSQL database in the same region as the web service and set `DATABASE_URL` to its internal connection URL.
3. Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` as private Render environment variables. Use a unique password of at least 12 characters.
4. Deploy the web service. The application creates its tables during startup.
5. From the service shell, run `flask --app run.py create-admin` once. Then remove `ADMIN_EMAIL` and `ADMIN_PASSWORD` from the service environment and redeploy.
6. Open `/admin/login` on the Render URL and test login, project management, profile updates/uploads, contact messages, and logout.

Build command: `pip install -r requirements.txt`

Start command: `gunicorn --bind 0.0.0.0:$PORT run:app`

Health check: `/`

Uploads: the Blueprint mounts a persistent disk at `/var/data` and writes files to `/var/data/uploads`.

Production environment variables: `APP_ENV=production`, `SECRET_KEY`, `COOKIE_SECURE=1`, `DATABASE_URL`, `UPLOAD_FOLDER=/var/data/uploads`, and temporary one-time `ADMIN_EMAIL`/`ADMIN_PASSWORD` during first-admin creation.

## Live demo

Deployment is not configured yet. The public portfolio URL will be added here after deployment.

## Connect with me

- GitHub: [github.com/Ace0th](https://github.com/Ace0th)
- LinkedIn: [Md Alamin Sk](https://www.linkedin.com/in/md-alamin-sk-a0b957422)

## LinkedIn Featured section

**Title:** Personal Portfolio — Md Alamin Sk

**Description:** Personal developer portfolio showcasing my projects, technical skills, and experience building web applications with Python, Flask, HTML, CSS and JavaScript.

**URL:** Add the public portfolio URL after deployment.

## Optional LinkedIn post

I’ve built my personal portfolio website to share my projects, technical interests, and what I’m learning.

It’s built with Python, Flask, HTML, CSS, and JavaScript, with a private admin dashboard for dynamic project management, a responsive layout, and a database-backed contact form.

I’m currently learning more about advanced Python, Flask, REST APIs, SQL/databases, and AI/ML. I’m looking forward to continuing to learn by building useful software.

Portfolio: add the public URL after deployment

GitHub: https://github.com/Ace0th/personal-portfolio

## Repository details

Repository name: `personal-portfolio`

Description: `Personal portfolio website built with Python, Flask, HTML, CSS and JavaScript.`

Suggested topics: `python`, `flask`, `portfolio`, `web-development`, `full-stack`, `sqlalchemy`, `html`, `css`, `javascript`
