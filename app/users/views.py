from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from users.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .utils import send_password_reset_email

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .utils import send_password_reset_email
User = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_users(request):
    users = User.objects.filter(is_superuser=False)
    return Response({
        "count": users.count(),
        "results": list(users.values("id", "email", "name"))  # ← username ➜ name
    })


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageApiView(generics.RetrieveUpdateAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # GET -> profil “léger” (email + name) pour coller à tes tests
        if self.request.method in ("GET",):
            return ProfileSerializer
        # PATCH/PUT -> serializer complet
        return UserSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def get_object(self):
        return self.request.user


# === Password Reset (pro) ===

@api_view(["POST"])
def request_password_reset(request):
    """Étape 1 : demander la réinitialisation"""
    email = request.data.get("email")
    if not email:
        return Response({"message": "Veuillez fournir un email."}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Pour la sécurité, ne pas révéler si l'utilisateur existe
        return Response({"message": "Si l’email existe, un mail de réinitialisation a été envoyé."})

    try:
        send_password_reset_email(user)
    except Exception as e:
        return Response({"message": f"Erreur lors de l'envoi de l'e-mail: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Si l’email existe, un mail de réinitialisation a été envoyé."}, status=status.HTTP_200_OK)

@api_view(["POST"])
def reset_password(request):
    """Étape 2 : réinitialiser le mot de passe via uid et token"""
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    re_new_password = request.data.get("re_new_password")

    if not all([uid, token, new_password, re_new_password]):
        return Response({"message": "Tous les champs sont requis (uid, token, new_password, re_new_password)."}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != re_new_password:
        return Response({"message": "Les mots de passe ne correspondent pas."}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    try:
        uid_decoded = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=uid_decoded)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"message": "Utilisateur introuvable."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"message": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)