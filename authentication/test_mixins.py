from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User


class AuthenticatedTestMixin:
    """Mixin para facilitar testes com autenticação JWT"""

    def create_test_user(
        self,
        username="testuser",
        email="test@example.com",
        password="testpass123",  # nosec B107
    ):
        """Cria um usuário de teste"""
        return User.objects.create_user(
            username=username, email=email, password=password
        )

    def authenticate_user(self, user=None):
        """Autentica um usuário nos testes"""
        if user is None:
            user = self.create_test_user()

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return user

    def clear_authentication(self):
        """Remove autenticação dos testes"""
        self.client.credentials()
