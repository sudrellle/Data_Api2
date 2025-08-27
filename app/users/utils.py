import io
import logging
import qrcode
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)

def make_reset_payload(user):
    """Génère uid, token et lien complet de réinitialisation"""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/password-reset/confirm/{uidb64}/{token}"
    return uidb64, token, reset_url

def generate_qr_bytes(data: str) -> bytes:
    """Génère le QR code en bytes"""
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def send_password_reset_email(user):
    """Envoie un e-mail pro de réinitialisation"""
    uid, token, reset_url = make_reset_payload(user)

    subject = "🔐 Réinitialisation de votre mot de passe"
    body = (
        f"Bonjour {user.name or user.email},\n\n"
        "Vous avez demandé la réinitialisation de votre mot de passe.\n"
        "Pour le modifier, vous avez 2 options :\n\n"
        f"1️⃣ Copier ces informations pour l’API :\n"
        f"   uid: {uid}\n"
        f"   token: {token}\n\n"
        f"2️⃣ Ou utiliser ce lien direct :\n{reset_url}\n\n"
        "⚠️ Ce lien/jeton expire dans 1 heure.\n"
        "Si vous n'avez pas fait cette demande, ignorez ce mail."
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    # QR code optionnel
    try:
        email.attach("reset_qr.png", generate_qr_bytes(reset_url), "image/png")
    except Exception as e:
        logger.warning(f"Impossible de joindre le QR code : {e}")

    try:
        email.send(fail_silently=False)
        logger.info(f"Email de reset envoyé à {user.email}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email : {e}")
        raise e
