"""
Testes de throttling específicos para profissionais
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings, tag
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from profissionais.models import Profissional


@tag('throttling', 'integration')
class ProfissionalThrottlingDetailedTestCase(APITestCase):
    """Testes detalhados para throttling de profissionais"""

    def setUp(self):
        """Configurar dados de teste"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Criar alguns profissionais existentes
        self.profissional1 = Profissional.objects.create(
            nome="Dr. João Silva",
            email="joao@example.com",
            especialidade="Cardiologia",
            telefone="11987654321",
        )

        self.profissional2 = Profissional.objects.create(
            nome="Dra. Maria Santos",
            email="maria@example.com",
            especialidade="Dermatologia",
            telefone="11876543210",
        )

        self.list_url = reverse("profissional-list")
        self.detail_url = reverse(
            "profissional-detail", kwargs={"pk": self.profissional1.id}
        )

        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_retrieve_not_throttled(self):
        """Testa que retrieve (detalhes) não é throttled"""
        # Fazer várias requests de detalhe - não devem ser limitadas
        for i in range(10):
            response = self.client.get(self.detail_url)
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Retrieve request {i + 1} foi throttled quando não deveria",
            )

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "profissional_create": "2/min",  # Permite 2 criações por minuto
            },
        }
    )
    def test_create_and_update_throttling_separate(self):
        """Testa que criação e atualização compartilham mesmo limite"""
        self.client.force_authenticate(user=self.user)

        create_data = {
            "nome": "Dr. Novo",
            "email": "novo@example.com",
            "especialidade": "Pediatria",
            "telefone": "31987654321",
        }

        # Primeira criação
        response1 = self.client.post(self.list_url, create_data)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Segunda criação
        create_data["email"] = "novo2@example.com"
        response2 = self.client.post(self.list_url, create_data)
        self.assertNotEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Terceira criação deve ser throttled
        create_data["email"] = "novo3@example.com"
        response3 = self.client.post(self.list_url, create_data)
        self.assertEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "listing": "3/min",
            },
        }
    )
    def test_listing_with_filters_still_throttled(self):
        """Testa que listagem com filtros ainda é throttled"""
        # Request 1: sem filtro
        response1 = self.client.get(self.list_url)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 2: com filtro de telefone (se disponível)
        response2 = self.client.get(self.list_url, {"email__contains": "example"})
        self.assertNotEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 3: com filtro de especialidade
        response3 = self.client.get(self.list_url, {"especialidade": "Cardiologia"})
        self.assertNotEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 4: deve ser throttled
        response4 = self.client.get(self.list_url)
        self.assertEqual(response4.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_authenticated_vs_anonymous_different_limits(self):
        """Testa que usuários autenticados e anônimos têm limites diferentes"""
        with override_settings(
            REST_FRAMEWORK={
                "DEFAULT_THROTTLE_CLASSES": [
                    "rest_framework.throttling.AnonRateThrottle",
                    "rest_framework.throttling.UserRateThrottle",
                ],
                "DEFAULT_THROTTLE_RATES": {
                    "anon": "1/min",  # Anônimos: 1/min
                    "user": "5/min",  # Autenticados: 5/min
                    "listing": "100/min",  # Sem limite prático para listing
                },
            }
        ):
            # Como usuário anônimo: uma request
            response1 = self.client.get(self.list_url)
            self.assertNotEqual(
                response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS
            )

            # Segunda request anônima: deve ser throttled
            response2 = self.client.get(self.list_url)
            self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

            # Limpar cache e autenticar
            cache.clear()
            self.client.force_authenticate(user=self.user)

            # Como usuário autenticado: múltiplas requests devem passar
            for i in range(3):
                response = self.client.get(self.list_url)
                self.assertNotEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"Authenticated request {i + 1} foi throttled",
                )


@tag('throttling', 'integration') 
class ProfissionalThrottlingErrorHandlingTestCase(APITestCase):
    """Testes para verificar o tratamento correto de erros de throttling"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "anon": "1/min",
            },
        }
    )
    def test_throttle_error_response_format(self):
        """Testa se a resposta de erro de throttling tem o formato correto"""
        list_url = reverse("profissional-list")

        # Primeira request
        self.client.get(list_url)

        # Segunda request: deve ser throttled
        response2 = self.client.get(list_url)

        if response2.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            # Verificar formato da resposta
            self.assertIn("detail", response2.data)
            self.assertIsInstance(response2.data["detail"], str)

            # Verificar cabeçalho Retry-After
            self.assertIn("Retry-After", response2)
            retry_after = response2["Retry-After"]
            self.assertTrue(int(retry_after) > 0)

            # Verificar que a mensagem é informativa
            detail = response2.data["detail"].lower()
            self.assertTrue(
                "throttled" in detail or "too many" in detail or "rate limit" in detail
            )
