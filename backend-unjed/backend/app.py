"""
Backend UNJED-BENIN — API Flask.

Sert :
- l'authentification des administrateurs (comptes individuels)
- la publication d'annonces / documents / liens / images / vidéos
- l'inscription des abonnés (avec notification email, une fois configurée)

Le site vitrine (GitHub Pages) appelle cette API en JavaScript (fetch),
depuis un autre domaine — d'où la configuration CORS ci-dessous.
"""
import os
import uuid
from functools import wraps

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import db, Admin, Post, Subscriber
from emailer import notify_admin_new_subscriber, confirm_subscription

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "webp",          # images
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",  # documents
    "mp4", "webm", "mov",                          # vidéos uploadées directement
}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 Mo par fichier

# Origines autorisées à appeler cette API (le site GitHub Pages).
# A ajuster si le site change de domaine (nom de domaine personnalisé, etc).
ALLOWED_ORIGINS = [
    "https://theophiledounon-dotcom.github.io",
    "http://127.0.0.1:5500",   # pratique pour tester le site en local (Live Server)
    "http://localhost:5500",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-moi-avec-une-vraie-cle-secrete")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'unjed.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Cookies de session cross-domain (backend PythonAnywhere <-> frontend GitHub Pages)
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True  # nécessite HTTPS (PythonAnywhere le fournit)

db.init_app(app)
CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return jsonify({"error": "Non authentifié"}), 401
        return view(*args, **kwargs)
    return wrapped


@app.post("/api/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        return jsonify({"error": "Identifiants incorrects"}), 401

    session["admin_id"] = admin.id
    session.permanent = True
    return jsonify({"ok": True, "admin": admin.to_dict()})


@app.post("/api/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return jsonify({"ok": True})


@app.get("/api/admin/me")
def admin_me():
    admin_id = session.get("admin_id")
    if not admin_id:
        return jsonify({"admin": None})
    admin = db.session.get(Admin, admin_id)
    return jsonify({"admin": admin.to_dict() if admin else None})


# ---------------------------------------------------------------------------
# Publications (annonces / documents / liens / images / vidéos)
# ---------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/api/posts")
def list_posts():
    """
    Liste des publications.
    - ?visibility=public  -> uniquement le contenu public (pour le site, ex. actualités)
    - sans authentification admin, jamais renvoyer le contenu "members"
    """
    visibility = request.args.get("visibility")
    query = Post.query.order_by(Post.created_at.desc())

    if session.get("admin_id"):
        # Un admin connecté peut tout voir (utile pour gérer l'espace admin)
        if visibility:
            query = query.filter_by(visibility=visibility)
    else:
        # Public : uniquement le contenu public, quoi qu'il arrive
        query = query.filter_by(visibility="public")

    posts = query.limit(100).all()
    return jsonify([p.to_dict() for p in posts])


@app.post("/api/posts")
@login_required
def create_post():
    title = (request.form.get("title") or "").strip()
    body = request.form.get("body") or ""
    post_type = request.form.get("post_type") or "announcement"
    visibility = request.form.get("visibility") or "members"
    external_url = (request.form.get("external_url") or "").strip() or None

    if not title:
        return jsonify({"error": "Le titre est obligatoire"}), 400
    if post_type not in {"announcement", "document", "link", "image", "video"}:
        return jsonify({"error": "Type de publication invalide"}), 400
    if visibility not in {"public", "members"}:
        return jsonify({"error": "Visibilité invalide"}), 400

    file_url = None
    uploaded_file = request.files.get("file")
    if uploaded_file and uploaded_file.filename:
        if not allowed_file(uploaded_file.filename):
            return jsonify({"error": "Type de fichier non autorisé"}), 400
        ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        uploaded_file.save(os.path.join(UPLOAD_DIR, stored_name))
        file_url = f"/static/uploads/{stored_name}"

    post = Post(
        title=title,
        body=body,
        post_type=post_type,
        visibility=visibility,
        file_url=file_url,
        external_url=external_url,
        author_id=session["admin_id"],
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201


@app.delete("/api/posts/<int:post_id>")
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Introuvable"}), 404
    if post.file_url:
        file_path = os.path.join(BASE_DIR, post.file_url.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"ok": True})


@app.get("/static/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ---------------------------------------------------------------------------
# Abonnés (newsletter / notifications)
# ---------------------------------------------------------------------------
@app.post("/api/subscribe")
def subscribe():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if "@" not in email or "." not in email:
        return jsonify({"error": "Email invalide"}), 400

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({"ok": True, "already": True})

    sub = Subscriber(email=email)
    db.session.add(sub)
    db.session.commit()

    # Emails best-effort : n'empêchent jamais l'inscription de réussir
    notify_admin_new_subscriber(email)
    confirm_subscription(email)

    return jsonify({"ok": True, "already": False})


@app.get("/api/admin/subscribers")
@login_required
def list_subscribers():
    subs = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return jsonify([s.to_dict() for s in subs])


# ---------------------------------------------------------------------------
# Emplacement réservé : PAIEMENT ADHESION (FedaPay / Kkiapay)
# ---------------------------------------------------------------------------
# A implémenter une fois le compte marchand créé. Le flux prévu :
#   1. POST /api/adhesion/initier  -> crée la demande en base (statut "en_attente")
#                                     + appelle l'API FedaPay/Kkiapay pour générer
#                                     un lien de paiement, renvoyé au frontend.
#   2. Le membre paie sur la page FedaPay/Kkiapay.
#   3. FedaPay/Kkiapay appelle notre webhook POST /api/adhesion/webhook
#      pour confirmer le paiement -> on passe le statut à "payé" et on envoie
#      les 2 emails (confirmation membre + notification admin).
#
# @app.post("/api/adhesion/initier")
# def initier_adhesion(): ...
#
# @app.post("/api/adhesion/webhook")
# def webhook_paiement(): ...


# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
