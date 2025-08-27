from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="reset@example.com",
            password="OldPass123!",
            name="Reset User",
            genre="F",
            date_naissance="2000-01-01",
            is_active=True,
        )

    def test_request_reset_always_200(self):
        url = reverse("user:password_reset")
        res = self.client.post(url, {"email": "reset@example.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res2 = self.client.post(url, {"email": "inconnu@example.com"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_confirm_reset_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = reverse("user:password_reset_confirm")
        payload = {
            "uid": uid,
            "token": token,
            "new_password": "NewPass123!",
            "re_new_password": "NewPass123!",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123!"))

    def test_confirm_reset_bad_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("user:password_reset_confirm")
        payload = {
            "uid": uid,
            "token": "not-a-valid-token",
            "new_password": "NewPass123!",
            "re_new_password": "NewPass123!",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
