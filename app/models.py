from datetime import datetime, timezone
from . import db


def now_utc():
    return datetime.now(timezone.utc)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc, nullable=False)


class SiteProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=1)
    full_name = db.Column(db.String(120), nullable=False, default="Md Alamin Sk")
    role = db.Column(db.String(160), nullable=False, default="B.Tech CSE (AI & ML) Student | Python & Flask Developer")
    introduction = db.Column(db.String(320), nullable=False, default="Building practical web applications, AI-powered solutions, and meaningful digital experiences.")
    github_url = db.Column(db.String(500), nullable=False, default="https://github.com/Ace0th")
    linkedin_url = db.Column(db.String(500), nullable=False, default="https://www.linkedin.com/in/md-alamin-sk-a0b957422")
    image_path = db.Column(db.String(500), nullable=False, default="")
    updated_at = db.Column(db.DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    short_description = db.Column(db.String(240), nullable=False)
    full_description = db.Column(db.Text, nullable=False, default="")
    thumbnail = db.Column(db.String(500), nullable=False, default="")
    technologies = db.Column(db.JSON, nullable=False, default=list)
    category = db.Column(db.String(40), nullable=False, default="Web Development")
    github_url = db.Column(db.String(500), nullable=False, default="")
    live_url = db.Column(db.String(500), nullable=False, default="")
    featured = db.Column(db.Boolean, nullable=False, default=False)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    published = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    subject = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc, nullable=False)
