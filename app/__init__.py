import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    load_dotenv(ROOT / ".env")
    secret_key = os.getenv("SECRET_KEY")
    if os.getenv("APP_ENV") == "production" and not secret_key:
        raise RuntimeError("Set SECRET_KEY in the environment before running in production.")
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SECRET_KEY=secret_key or "local-only-change-me",
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", f"sqlite:///{Path(app.instance_path) / 'portfolio.db'}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", str(ROOT / "app" / "static" / "uploads")),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("APP_ENV") == "production" or os.getenv("COOKIE_SECURE", "0") == "1",
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    from . import models  # noqa: F401
    from .routes import bp
    app.register_blueprint(bp)

    @app.context_processor
    def csrf_context():
        from flask import session
        import secrets
        session.setdefault("csrf", secrets.token_urlsafe(32))
        from datetime import datetime
        from .models import SiteProfile
        return {"csrf_token": session["csrf"], "current_year": datetime.now().year, "profile": db.session.get(SiteProfile, 1)}

    @app.cli.command("create-admin")
    def create_admin():
        """Create the first administrator from ADMIN_EMAIL and ADMIN_PASSWORD."""
        from .models import Admin
        from werkzeug.security import generate_password_hash
        with app.app_context():
            db.create_all()
            if Admin.query.first():
                raise SystemExit("An admin already exists; public signup is disabled.")
            email, password = os.getenv("ADMIN_EMAIL", "").strip().lower(), os.getenv("ADMIN_PASSWORD", "")
            if not email or len(password) < 12:
                raise SystemExit("Set ADMIN_EMAIL and an ADMIN_PASSWORD of at least 12 characters in portfolio/.env.")
            db.session.add(Admin(email=email, password_hash=generate_password_hash(password)))
            db.session.commit()
            print(f"Administrator created for {email}.")

    with app.app_context():
        db.create_all()
        from .models import Project, SiteProfile
        if db.session.get(SiteProfile, 1) is None:
            db.session.add(SiteProfile(id=1))
            db.session.commit()
        if Project.query.count() == 0:
            db.session.add(Project(
                title="Employee Management System",
                short_description="A full-stack employee management app for secure team records, role-based access, and employee administration.",
                full_description="Built with Flask and SQLAlchemy, this application provides administrator and employee workspaces, authentication, protected management tools, and a responsive interface.",
                technologies=["Python", "Flask", "SQLAlchemy", "PostgreSQL", "HTML", "CSS", "JavaScript"],
                category="Flask", github_url="https://github.com/Ace0th/Employee-Management-System",
                live_url="https://employee-management-system-hmwimrwb9-theofficialalamin-6057.vercel.app/",
                featured=True, display_order=1, published=True,
                thumbnail="https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=1200&q=80",
            ))
            db.session.commit()
    return app
