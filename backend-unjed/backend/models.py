"""
Modèles de base de données pour le backend UNJED-BENIN.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(db.Model):
    """Un compte administrateur (Théophile + responsables)."""
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
    Une publication faite par un admin : annonce, document, lien, image ou vidéo.
    - post_type: "announcement" | "document" | "link" | "image" | "video"
    - visibility: "public" (visible sur le site, ex. Actualités) | "members" (espace interne uniquement)
    - file_url: chemin du fichier uploadé (document/image/vidéo uploadée), sinon None
    - external_url: lien externe (ex. YouTube/Vimeo, ou lien libre), sinon None
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    post_type = db.Column(db.String(20), nullable=False, default="announcement")
    visibility = db.Column(db.String(10), nullable=False, default="members")
    file_url = db.Column(db.String(500), nullable=True)
    external_url = db.Column(db.String(500), nullable=True)
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
            "external_url": self.external_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": self.author.display_name if self.author else None,
        }


class Subscriber(db.Model):
    """Une personne qui s'est abonnée aux actualités du site."""
    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "created_at": self.created_at.isoformat()}
