import re
import secrets
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from . import db
from .models import Admin, ContactMessage, Project, SiteProfile

bp = Blueprint("portfolio", __name__)
CATEGORIES = ["Web Development", "Python", "Flask", "AI/ML", "UI/UX"]
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def is_admin():
    return bool(session.get("admin_id"))


def require_admin():
    if not is_admin():
        return redirect(url_for("portfolio.login", next=request.path))
    return None


def safe_url(value, label, required=False):
    value = (value or "").strip()
    if not value and not required:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Enter a valid {label} URL starting with https://.")
    return value[:500]


def project_payload(form, previous=None):
    title = form.get("title", "").strip()
    short = form.get("short_description", "").strip()
    full = form.get("full_description", "").strip()
    category = form.get("category", "Web Development").strip()
    tech = [part.strip()[:40] for part in form.get("technologies", "").split(",") if part.strip()]
    if not title or len(title) > 120: raise ValueError("Project title is required (up to 120 characters).")
    if not short or len(short) > 240: raise ValueError("Short description is required (up to 240 characters).")
    if len(full) > 8000: raise ValueError("Full description must be 8,000 characters or fewer.")
    if category not in CATEGORIES: raise ValueError("Choose a valid project category.")
    if len(tech) > 16: raise ValueError("Add up to 16 technologies.")
    project = previous or Project()
    project.title, project.short_description, project.full_description = title, short, full
    project.category, project.technologies = category, tech
    project.github_url = safe_url(form.get("github_url"), "GitHub", True)
    project.live_url = safe_url(form.get("live_url"), "live demo")
    project.featured = form.get("featured") == "on"
    project.published = form.get("published") == "on"
    try: project.display_order = max(0, min(10000, int(form.get("display_order", "0"))))
    except ValueError: raise ValueError("Display order must be a whole number.")
    project.thumbnail = safe_url(form.get("thumbnail"), "thumbnail") if form.get("thumbnail", "").strip().startswith(("http://", "https://")) else (form.get("thumbnail", "").strip() or (previous.thumbnail if previous else ""))
    upload = request.files.get("thumbnail_file")
    if upload and upload.filename:
        name = secure_filename(upload.filename)
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in ALLOWED_IMAGE_EXTENSIONS: raise ValueError("Upload a PNG, JPG, WebP, or GIF image.")
        name = f"{secrets.token_hex(12)}.{ext}"
        upload.save(Path(current_app.config["UPLOAD_FOLDER"]) / name)
        project.thumbnail = url_for("portfolio.uploaded_image", name=name)
    return project


@bp.get("/")
def home():
    projects = Project.query.filter_by(published=True).order_by(Project.featured.desc(), Project.display_order, Project.created_at.desc()).all()
    return render_template("index.html", projects=projects, categories=CATEGORIES)


@bp.get("/uploads/<path:name>")
def uploaded_image(name):
    if Path(name).name != name:
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name, conditional=True, max_age=3600)


@bp.post("/contact")
def contact():
    data = request.form
    name, email = data.get("name", "").strip(), data.get("email", "").strip().lower()
    subject, message = data.get("subject", "").strip(), data.get("message", "").strip()
    if not (1 <= len(name) <= 100 and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) and len(email) <= 254 and 1 <= len(subject) <= 160 and 10 <= len(message) <= 4000):
        flash("Please check your details. The message must be at least 10 characters.", "error")
    else:
        db.session.add(ContactMessage(name=name, email=email, subject=subject, message=message))
        db.session.commit()
        flash("Thanks for reaching out. Your message has been sent.", "success")
    return redirect(url_for("portfolio.home") + "#contact")


@bp.get("/admin/login")
def login():
    if is_admin(): return redirect(url_for("portfolio.dashboard"))
    return render_template("login.html")


@bp.post("/admin/login")
def login_post():
    if not secrets.compare_digest(request.form.get("csrf_token", ""), session.get("csrf", "")): abort(400)
    email = request.form.get("email", "").strip().lower()
    admin = Admin.query.filter_by(email=email).first()
    if not admin or not check_password_hash(admin.password_hash, request.form.get("password", "")):
        flash("Email or password is incorrect.", "error")
        return redirect(url_for("portfolio.login"))
    session.clear()
    session["admin_id"] = admin.id
    session["csrf"] = secrets.token_urlsafe(32)
    return redirect(url_for("portfolio.dashboard"))


@bp.before_app_request
def protect_admin_writes():
    if request.method == "POST":
        if not secrets.compare_digest(request.form.get("csrf_token", ""), session.get("csrf", "")): abort(400)
    if request.path.startswith("/admin/") and request.method == "POST" and request.endpoint != "portfolio.login_post":
        if not is_admin(): abort(401)


@bp.post("/admin/logout")
def logout():
    if not is_admin(): return redirect(url_for("portfolio.login"))
    session.clear()
    return redirect(url_for("portfolio.login"))


@bp.get("/admin")
def dashboard():
    denied = require_admin()
    if denied: return denied
    projects = Project.query.order_by(Project.display_order, Project.title).all()
    return render_template("admin.html", projects=projects, messages=ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(20).all())


@bp.route("/admin/profile", methods=["GET", "POST"])
def edit_profile():
    denied = require_admin()
    if denied: return denied
    profile = db.session.get(SiteProfile, 1)
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "").strip()
        introduction = request.form.get("introduction", "").strip()
        if not name or len(name) > 120 or not role or len(role) > 160 or not introduction or len(introduction) > 320:
            flash("Name, role, and introduction are required and must fit their length limits.", "error")
        else:
            try:
                github = safe_url(request.form.get("github_url"), "GitHub", True)
                linkedin = safe_url(request.form.get("linkedin_url"), "LinkedIn", True)
                profile.full_name, profile.role, profile.introduction = name, role, introduction
                profile.github_url, profile.linkedin_url = github, linkedin
                upload = request.files.get("profile_image")
                if upload and upload.filename:
                    disk_name = secure_filename(upload.filename)
                    ext = disk_name.rsplit(".", 1)[-1].lower() if "." in disk_name else ""
                    if ext not in ALLOWED_IMAGE_EXTENSIONS: raise ValueError("Upload a PNG, JPG, WebP, or GIF image.")
                    image_name = f"profile-{secrets.token_hex(12)}.{ext}"
                    upload.save(Path(current_app.config["UPLOAD_FOLDER"]) / image_name)
                    profile.image_path = url_for("portfolio.uploaded_image", name=image_name)
                db.session.commit()
                flash("Profile updated.", "success")
                return redirect(url_for("portfolio.edit_profile"))
            except ValueError as exc:
                flash(str(exc), "error")
    return render_template("profile_form.html", profile=profile)


@bp.route("/admin/projects/new", methods=["GET", "POST"])
@bp.route("/admin/projects/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id=None):
    denied = require_admin()
    if denied: return denied
    project = db.session.get(Project, project_id) if project_id else Project()
    if project_id and project is None: abort(404)
    if request.method == "POST":
        try:
            project = project_payload(request.form, project)
            if project_id is None: db.session.add(project)
            db.session.commit()
            flash("Project saved.", "success")
            return redirect(url_for("portfolio.dashboard"))
        except ValueError as exc:
            flash(str(exc), "error")
    return render_template("project_form.html", project=project, categories=CATEGORIES)


@bp.post("/admin/projects/<int:project_id>/delete")
def delete_project(project_id):
    denied = require_admin()
    if denied: return denied
    project = db.session.get(Project, project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted.", "success")
    return redirect(url_for("portfolio.dashboard"))
