"""
Testes de throttling para consultas
"""

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings, tag
from django.urls import reverse

from consultas.models import Consulta
from profissionais.models import Profissional


@tag("throttling", "integration")
class ConsultaThrottlingTestCase(APITestCase):
    """Testes para verificar throttling nas rotas de consulta"""

    def setUp(self):
        """Configurar dados de teste"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.profissional = Profissional.objects.create(
            nome="Dr. Test",
            email="dr.test@example.com",
            especialidade="Clínico Geral",
            telefone="11999999999",
        )

        self.list_url = reverse("consulta-list")
        self.consulta_data = {
            "profissional": self.profissional.id,
            "paciente_nome": "Paciente Teste",
            "data_hora": "2025-08-25T14:30:00",
            "observacoes": "Consulta de teste",
        }

        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "listing": "2/min",  # Limite baixo para teste
            },
        }
    )
    def test_consulta_list_throttling(self):
        """Testa throttling na listagem de consultas"""
        # Primeira request deve passar
        response1 = self.client.get(self.list_url)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Segunda request deve passar
        response2 = self.client.get(self.list_url)
        self.assertNotEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Terceira request deve ser throttled
        response3 = self.client.get(self.list_url)
        self.assertEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "consulta_create": "1/min",  # Limite muito baixo
            },
        }
    )
    def test_consulta_create_throttling(self):
        """Testa throttling na criação de consultas"""
        self.client.force_authenticate(user=self.user)

        # Primeira criação deve passar
        response1 = self.client.post(self.list_url, self.consulta_data)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Segunda criação deve ser throttled
        self.consulta_data["paciente_nome"] = "Outro Paciente"
        response2 = self.client.post(self.list_url, self.consulta_data)
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


@tag("throttling", "integration")
class ProfissionalThrottlingTestCase(APITestCase):
    """Testes para verificar throttling nas rotas de profissional"""

    def setUp(self):
        """Configurar dados de teste"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.list_url = reverse("profissional-list")
        self.profissional_data = {
            "nome": "Dr. Teste Throttling",
            "email": "dr.throttling@example.com",
            "especialidade": "Cardiologia",
            "telefone": "21987654321",
        }

        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "listing": "2/min",  # Limite baixo para teste
            },
        }
    )
    def test_profissional_list_throttling(self):
        """Testa throttling na listagem de profissionais"""
        # Primeira request deve passar
        response1 = self.client.get(self.list_url)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Segunda request deve passar
        response2 = self.client.get(self.list_url)
        self.assertNotEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Terceira request deve ser throttled
        response3 = self.client.get(self.list_url)
        self.assertEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "profissional_create": "1/min",  # Limite muito baixo
            },
        }
    )
    def test_profissional_create_throttling(self):
        """Testa throttling na criação de profissionais"""
        self.client.force_authenticate(user=self.user)

        # Primeira criação deve passar
        response1 = self.client.post(self.list_url, self.profissional_data)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Segunda criação deve ser throttled
        self.profissional_data["email"] = "outro.dr@example.com"
        response2 = self.client.post(self.list_url, self.profissional_data)
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


@tag("throttling", "integration")
class IntegratedThrottlingTestCase(APITestCase):
    """Testes de integração para throttling entre diferentes endpoints"""

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
                "anon": "3/min",  # Limite global baixo para teste
            },
        }
    )
    def test_global_anon_throttling_across_endpoints(self):
        """Testa se throttling anônimo funciona entre diferentes endpoints"""
        consulta_url = reverse("consulta-list")
        profissional_url = reverse("profissional-list")

        # Request 1: consulta
        response1 = self.client.get(consulta_url)
        self.assertNotEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 2: profissional
        response2 = self.client.get(profissional_url)
        self.assertNotEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 3: consulta novamente
        response3 = self.client.get(consulta_url)
        self.assertNotEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Request 4: deve ser throttled (global limit)
        response4 = self.client.get(profissional_url)
        self.assertEqual(response4.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
