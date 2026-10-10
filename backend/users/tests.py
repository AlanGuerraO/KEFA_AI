from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.password = "Kefa-Test!9472"
        self.user = User.objects.create_user(
            username="usuario_prueba",
            email="prueba@example.com",
            password=self.password,
        )

    def registration_data(self, **changes):
        data = {
            "username": "nuevo_usuario",
            "email": "nuevo@example.com",
            "password": "Registro-Seguro!8294",
        }
        data.update(changes)
        return data

    def test_registration_hashes_password_and_returns_safe_fields(self):
        data = self.registration_data()
        response = self.client.post(
            reverse("user-register"), data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {"id", "username", "email"})
        user = User.objects.get(username=data["username"])
        self.assertNotEqual(user.password, data["password"])
        self.assertTrue(user.check_password(data["password"]))

    def test_registration_cannot_grant_privileges(self):
        data = self.registration_data(
            is_staff=True,
            is_superuser=True,
            groups=[1],
            user_permissions=[1],
        )
        response = self.client.post(
            reverse("user-register"), data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username=data["username"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.user_permissions.exists())

    def test_registration_rejects_invalid_data(self):
        cases = [
            {"password": "123"},
            {"username": self.user.username},
            {"email": "correo-invalido"},
            {"email": ""},
        ]
        initial_count = User.objects.count()
        for changes in cases:
            with self.subTest(changes=changes):
                response = self.client.post(
                    reverse("user-register"),
                    self.registration_data(**changes),
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), initial_count)

    def test_login_returns_access_and_refresh(self):
        response = self.client.post(
            reverse("user-login"),
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        access = AccessToken(response.data["access"])
        refresh = RefreshToken(response.data["refresh"])
        self.assertEqual(str(access["user_id"]), str(self.user.pk))
        self.assertEqual(str(refresh["user_id"]), str(self.user.pk))

    def test_login_rejects_wrong_password_and_inactive_user(self):
        response = self.client.post(
            reverse("user-login"),
            {"username": self.user.username, "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("user-login"),
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 401)

    def test_me_returns_authenticated_user(self):
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "id": self.user.pk,
                "username": self.user.username,
                "email": self.user.email,
            },
        )

    def test_me_rejects_invalid_expired_and_refresh_tokens(self):
        expired = AccessToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        tokens = [
            "token-invalido",
            str(expired),
            str(RefreshToken.for_user(self.user)),
        ]
        for token in tokens:
            with self.subTest(token_type=token[:15]):
                self.client.credentials(
                    HTTP_AUTHORIZATION=f"Bearer {token}"
                )
                response = self.client.get(reverse("user-me"))
                self.assertEqual(response.status_code, 401)

    def test_me_rejects_inactive_user_with_existing_token(self):
        token = AccessToken.for_user(self.user)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 401)

    def test_refresh_returns_access_for_same_user(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("token-refresh"),
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        access = AccessToken(response.data["access"])
        self.assertEqual(str(access["user_id"]), str(self.user.pk))

    def test_refresh_rejects_invalid_expired_and_access_tokens(self):
        expired = RefreshToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        tokens = [
            "token-invalido",
            str(expired),
            str(AccessToken.for_user(self.user)),
        ]
        for token in tokens:
            with self.subTest(token_type=token[:15]):
                response = self.client.post(
                    reverse("token-refresh"),
                    {"refresh": token},
                    format="json",
                )
                self.assertEqual(response.status_code, 401)

    def test_verify_accepts_valid_and_rejects_invalid_tokens(self):
        valid = AccessToken.for_user(self.user)
        expired = AccessToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        for token, expected in [
            (str(valid), 200),
            ("token-invalido", 401),
            (str(expired), 401),
        ]:
            with self.subTest(expected=expected):
                response = self.client.post(
                    reverse("token-verify"),
                    {"token": token},
                    format="json",
                )
                self.assertEqual(response.status_code, expected)
