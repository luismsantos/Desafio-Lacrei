"""
Testes simplificados para verificar a configuração do throttling.
Estes testes verificam que as classes de throttling estão corretamente configuradas
e que o sistema funciona em produção (conforme demonstrado).
"""

from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.throttling import (
    ConsultaCreateRateThrottle,
    ListingRateThrottle,
    LoginRateThrottle,
    ProfissionalCreateRateThrottle,
    RegistrationRateThrottle,
    SensitiveDataRateThrottle,
)


class ThrottlingConfigurationTestCase(TestCase):
    """Testes para verificar se as classes de throttling estão configuradas corretamente."""

    def test_throttle_classes_exist(self):
        """Verifica se todas as classes de throttling existem e têm configuração correta."""
        throttle_classes = [
            LoginRateThrottle,
            RegistrationRateThrottle,
            ListingRateThrottle,
            ConsultaCreateRateThrottle,
            ProfissionalCreateRateThrottle,
            SensitiveDataRateThrottle,
        ]

        for throttle_class in throttle_classes:
            # Verificar se a classe pode ser instanciada
            throttle = throttle_class()
            self.assertIsNotNone(throttle)

            # Verificar se tem scope definido
            self.assertIsNotNone(throttle.scope)
            self.assertIsInstance(throttle.scope, str)

    def test_login_throttle_configuration(self):
        """Testa configuração específica do LoginRateThrottle."""
        throttle = LoginRateThrottle()
        self.assertEqual(throttle.scope, "login")

    def test_registration_throttle_configuration(self):
        """Testa configuração específica do RegistrationRateThrottle."""
        throttle = RegistrationRateThrottle()
        self.assertEqual(throttle.scope, "registration")

    def test_listing_throttle_configuration(self):
        """Testa configuração específica do ListingRateThrottle."""
        throttle = ListingRateThrottle()
        self.assertEqual(throttle.scope, "listing")

    def test_consulta_create_throttle_configuration(self):
        """Testa configuração específica do ConsultaCreateRateThrottle."""
        throttle = ConsultaCreateRateThrottle()
        self.assertEqual(throttle.scope, "consulta_create")

    def test_profissional_create_throttle_configuration(self):
        """Testa configuração específica do ProfissionalCreateRateThrottle."""
        throttle = ProfissionalCreateRateThrottle()
        self.assertEqual(throttle.scope, "profissional_create")

    def test_sensitive_data_throttle_configuration(self):
        """Testa configuração específica do SensitiveDataRateThrottle."""
        throttle = SensitiveDataRateThrottle()
        self.assertEqual(throttle.scope, "sensitive_data")


class ThrottlingIntegrationSimpleTestCase(APITestCase):
    """Testes simples que verificam se o throttling não quebra as rotas básicas."""

    def setUp(self):
        """Setup para testes básicos."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_login_route_accepts_requests(self):
        """Verifica se a rota de login aceita requests normalmente."""
        url = reverse("auth-entrar")
        login_data = {"nome_usuario": "testuser", "senha": "testpass123"}

        response = self.client.post(url, login_data, format="json")
        # Deve retornar 200 (sucesso) ou 400 (erro de validação), não 500 (erro de servidor)
        self.assertIn(response.status_code, [200, 400])

    def test_registration_route_accepts_requests(self):
        """Verifica se a rota de registro aceita requests normalmente."""
        url = reverse("auth-registrar")
        register_data = {
            "username": "newuser",
            "email": "new@example.com",
            "senha": "newpass123",
            "confirmar_senha": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(url, register_data, format="json")
        # Deve retornar 201 (criado) ou 400 (erro de validação), não 500 (erro de servidor)
        self.assertIn(response.status_code, [201, 400])

    def test_profissionais_listing_route_works(self):
        """Verifica se a rota de listagem de profissionais funciona."""
        url = reverse("profissional-list")

        response = self.client.get(url)
        # Deve retornar 200 (sucesso), não 500 (erro de servidor)
        self.assertEqual(response.status_code, 200)

    def test_consultas_listing_route_works(self):
        """Verifica se a rota de listagem de consultas funciona."""
        url = reverse("consulta-list")

        response = self.client.get(url)
        # Pode retornar 401 (não autenticado) ou 200, mas não 500
        self.assertIn(response.status_code, [200, 401, 403])
