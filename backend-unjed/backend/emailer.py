"""
Envoi d'emails - UNJED-BENIN.

CONFIGURATION A FAIRE PLUS TARD (jamais dans le code, toujours en variables
d'environnement sur PythonAnywhere, onglet "Web" > "Environment variables") :

  MAIL_SERVER    = smtp.gmail.com          (si Gmail)
  MAIL_PORT      = 587
  MAIL_USERNAME  = unjedbenin@gmail.com     (l'adresse dédiée de l'ONG)
  MAIL_PASSWORD  = <mot de passe d'application Gmail, PAS le mot de passe normal>
  MAIL_FROM      = unjedbenin@gmail.com

Pour un mot de passe d'application Gmail : compte Google > Sécurité >
Validation en 2 étapes (à activer) > Mots de passe des applications.

Tant que ces variables ne sont pas configurées, les emails ne sont PAS
envoyés : la fonction log simplement un message dans la console (aucune
erreur, aucun blocage du reste du site).
"""
import os
import smtplib
from email.mime.text import MIMEText

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_FROM = os.environ.get("MAIL_FROM", MAIL_USERNAME)

ADMIN_NOTIFY_EMAIL = os.environ.get("ADMIN_NOTIFY_EMAIL", MAIL_USERNAME)


def _is_configured():
    return all([MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM])


def send_email(to_address, subject, body):
    """Envoie un email texte simple. Ne lève jamais d'exception vers l'appelant."""
    if not _is_configured():
        print(f"[emailer] Email NON envoyé (config manquante) -> to={to_address} subject={subject}")
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = MAIL_FROM
        msg["To"] = to_address
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, [to_address], msg.as_string())
        return True
    except Exception as exc:
        print(f"[emailer] Erreur d'envoi vers {to_address}: {exc}")
        return False


def notify_admin_new_subscriber(subscriber_email):
    send_email(
        ADMIN_NOTIFY_EMAIL,
        "Nouvel abonné UNJED-BENIN",
        f"Un nouvel abonné a rejoint la liste : {subscriber_email}",
    )


def confirm_subscription(subscriber_email):
    send_email(
        subscriber_email,
        "Confirmation d'abonnement — UNJED-BENIN",
        "Merci de vous être abonné aux actualités de l'UNJED-BENIN.\n\n"
        "Vous recevrez nos prochaines annonces et actualités directement par email.\n\n"
        "L'équipe UNJED-BENIN",
    )


def notify_admin_new_membership(applicant_name, applicant_email):
    send_email(
        ADMIN_NOTIFY_EMAIL,
        "Nouvelle demande d'adhésion — UNJED-BENIN",
        f"Nouvelle demande d'adhésion reçue de {applicant_name} ({applicant_email}).",
    )


def confirm_membership_payment(applicant_email, applicant_name, amount_fcfa):
    send_email(
        applicant_email,
        "Confirmation de paiement — UNJED-BENIN",
        f"Bonjour {applicant_name},\n\n"
        f"Nous confirmons la réception de votre paiement de {amount_fcfa} FCFA "
        "pour votre demande d'adhésion à l'UNJED-BENIN.\n\n"
        "Votre dossier va maintenant être examiné par le Bureau Exécutif National.\n\n"
        "L'équipe UNJED-BENIN",
    )
