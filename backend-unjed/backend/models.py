"""
Modèles de base de données pour le backend UNJED-BENIN.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(db.Model):
    """Compte administrateur sécurisé."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "display_name": self.display_name}


class Post(db.Model):
    """
    Publications des administrateurs :
    - 'announcement' : Annonces textuelles / communiqués (vers Actualités)
    - 'decision'     : Décisions officielles avec fichier PDF téléchargeable (vers Actualités)
    - 'image'        : Photos des activités (vers Multimédia)
    - 'video'        : Vidéos des activités (vers Multimédia)
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    post_type = db.Column(db.String(30), nullable=False, default="announcement")
    visibility = db.Column(db.String(10), nullable=False, default="public")
    file_url = db.Column(db.String(500), nullable=True)
    original_filename = db.Column(db.String(255), nullable=True)  # Nom du PDF pour le téléchargement
    external_url = db.Column(db.String(500), nullable=True)      # Lien YouTube / vidéo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)

    author = db.relationship("Admin")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "post_type": self.post_type,
            "visibility": self.visibility,
            "file_url": self.file_url,
            "original_filename": self.original_filename,
            "external_url": self.external_url,
            "created_at": self.created_at.strftime("%d %B %Y") if self.created_at else None,
            "author": self.author.display_name if self.author else "Bureau Exécutif",
        }


class Member(db.Model):
    """Adhésions reçues en ligne."""
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    member_type = db.Column(db.String(50), default="Personne physique")
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    dept_or_region = db.Column(db.String(100), nullable=True)
    profile = db.Column(db.String(100), nullable=False)
    motivation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "member_type": self.member_type,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "country": self.country,
            "dept_or_region": self.dept_or_region,
            "profile": self.profile,
            "motivation": self.motivation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ContactMessage(db.Model):
    """Messages envoyés depuis la page Contact."""
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
