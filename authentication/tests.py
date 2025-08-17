from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationAPITest(APITestCase):
    """Testes para API de autenticação"""

    def setUp(self):
        self.register_url = reverse("auth-registrar")
        self.login_url = reverse("auth-entrar")
        self.logout_url = reverse("auth-sair")
        self.profile_url = reverse("auth-perfil")

        # Usuário de teste
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # nosec B106
            first_name="Test",
            last_name="User",
        )

    def test_user_registration_success(self):
        """Testa registro de usuário com sucesso"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "senha": "newpass123",
            "confirmar_senha": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("usuario", response.data)
        self.assertEqual(response.data["usuario"]["nome_usuario"], "newuser")

    def test_user_registration_password_mismatch(self):
        """Testa registro com senhas diferentes"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "senha": "newpass123",
            "confirmar_senha": "differentpass",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_username(self):
        """Testa registro com username já existente"""
        data = {
            "username": "testuser",  # Já existe
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Testa registro com email já existente"""
        data = {
            "username": "newuser",
            "email": "test@example.com",  # Já existe
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Testa login com credenciais válidas"""
        data = {"nome_usuario": "testuser", "senha": "testpass123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("usuario", response.data)

    def test_user_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        data = {"nome_usuario": "testuser", "senha": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_authenticated(self):
        """Testa acesso ao perfil com usuário autenticado"""
        refresh = RefreshToken.for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_user_profile_unauthenticated(self):
        """Testa acesso ao perfil sem autenticação"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_update(self):
        """Testa atualização do perfil"""
        refresh = RefreshToken.for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_user_logout(self):
        """Testa logout do usuário"""
        refresh = RefreshToken.for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        data = {"refresh": str(refresh)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
