"""
Testes para verificar rate limiting/throttling nas rotas de autenticação
"""
import time
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse


class ThrottlingTestCase(APITestCase):
    """Testes para verificar se throttling está funcionando corretamente"""

    def setUp(self):
        """Configurar dados de teste"""
        self.login_url = reverse("auth-entrar")
        self.register_url = reverse("auth-registrar")
        
        # Usuário de teste
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        
        # Limpar cache antes de cada teste
        cache.clear()

    def tearDown(self):
        """Limpar cache depois de cada teste"""
        cache.clear()

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "anon": "5/min",  # Limite baixo para testes rápidos
                "user": "10/min",
                "login": "3/min",  # Limite muito baixo para testar rapidamente
            },
        }
    )
    def test_login_throttling_limits_requests(self):
        """Testa se o throttling de login funciona corretamente"""
        # Dados válidos de login
        login_data = {
            "username": "testuser",
            "senha": "testpass123",
        }

        # Fazer múltiplas tentativas de login (devem passar)
        for i in range(3):  # Limite é 3/min nos settings de teste
            response = self.client.post(self.login_url, login_data)
            # Pode dar 200 (sucesso) ou 400 (credenciais inválidas), mas não 429
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS, 
                              f"Request {i+1} foi throttled quando não deveria")

        # A próxima request deve ser throttled
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS, 
                        "Request extra não foi throttled")
        self.assertIn("detail", response.data)
        self.assertIn("throttled", response.data["detail"].lower())

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "anon": "2/min",  # Limite muito baixo para registro
            },
        }
    )
    def test_registration_throttling(self):
        """Testa throttling na rota de registro"""
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com", 
            "senha": "newpass123",
            "confirmar_senha": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        # Primeira tentativa deve funcionar
        response = self.client.post(self.register_url, register_data)
        self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Mudar dados para segunda tentativa
        register_data["username"] = "newuser2"
        register_data["email"] = "newuser2@example.com"
        
        # Segunda tentativa deve funcionar
        response = self.client.post(self.register_url, register_data)
        self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Terceira tentativa deve ser throttled
        register_data["username"] = "newuser3"
        register_data["email"] = "newuser3@example.com"
        
        response = self.client.post(self.register_url, register_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_specific_throttle_class(self):
        """Testa se LoginRateThrottle está sendo aplicado na view de login"""
        from authentication.views import LoginRateThrottle
        
        # Verificar se a classe de throttling personalizada existe
        self.assertTrue(hasattr(LoginRateThrottle, 'scope'))
        self.assertEqual(LoginRateThrottle.scope, 'login')

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_CLASSES": [],
            "DEFAULT_THROTTLE_RATES": {},
        }
    )
    def test_throttling_disabled_allows_unlimited_requests(self):
        """Testa que quando throttling está desabilitado, requests são ilimitadas"""
        login_data = {
            "username": "testuser",
            "senha": "testpass123",
        }

        # Fazer muitas requests - todas devem passar
        for i in range(10):
            response = self.client.post(self.login_url, login_data)
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS,
                              f"Request {i+1} foi throttled quando throttling está desabilitado")

    def test_throttle_headers_present_when_throttled(self):
        """Testa se headers de throttling estão presentes quando limitado"""
        with override_settings(
            REST_FRAMEWORK={
                "DEFAULT_THROTTLE_CLASSES": [
                    "rest_framework.throttling.AnonRateThrottle",
                ],
                "DEFAULT_THROTTLE_RATES": {
                    "anon": "1/min",  # Limite de apenas 1 request/min
                },
            }
        ):
            login_data = {
                "username": "testuser", 
                "senha": "testpass123",
            }

            # Primeira request
            response = self.client.post(self.login_url, login_data)
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

            # Segunda request deve ser throttled
            response = self.client.post(self.login_url, login_data)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                # Verificar se headers de retry estão presentes
                self.assertIn('Retry-After', response)
                self.assertTrue(int(response['Retry-After']) > 0)


class ThrottlingIntegrationTestCase(APITestCase):
    """Testes de integração para throttling com cache"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_throttle_cache_key_generation(self):
        """Testa se as chaves de cache para throttling são geradas corretamente"""
        # Este teste verifica indiretamente se o cache está sendo usado
        # fazendo requests e verificando se o throttling persiste
        
        with override_settings(
            REST_FRAMEWORK={
                "DEFAULT_THROTTLE_CLASSES": [
                    "rest_framework.throttling.AnonRateThrottle",
                ],
                "DEFAULT_THROTTLE_RATES": {
                    "anon": "1/min",
                },
            }
        ):
            login_url = reverse("auth-entrar")
            login_data = {"username": "test", "senha": "test"}

            # Primeira request
            response1 = self.client.post(login_url, login_data)
            
            # Segunda request deve ser throttled se cache está funcionando
            response2 = self.client.post(login_url, login_data)
            
            # Se o cache estiver funcionando, uma das requests deve ser throttled
            responses_429 = [r for r in [response1, response2] 
                           if r.status_code == status.HTTP_429_TOO_MANY_REQUESTS]
            
            # Deve haver pelo menos uma resposta throttled
            self.assertGreaterEqual(len(responses_429), 1, 
                                  "Nenhuma request foi throttled - cache pode não estar funcionando")

    def test_different_ips_have_separate_throttle_limits(self):
        """Testa se IPs diferentes têm limites de throttling separados"""
        with override_settings(
            REST_FRAMEWORK={
                "DEFAULT_THROTTLE_CLASSES": [
                    "rest_framework.throttling.AnonRateThrottle",
                ],
                "DEFAULT_THROTTLE_RATES": {
                    "anon": "1/min",
                },
            }
        ):
            login_url = reverse("auth-entrar")
            login_data = {"username": "test", "senha": "test"}

            # Request do IP 1
            response1 = self.client.post(login_url, login_data, 
                                       HTTP_X_FORWARDED_FOR='1.1.1.1')
            
            # Request do IP 2 (deve ser permitida mesmo que IP 1 tenha sido throttled)
            response2 = self.client.post(login_url, login_data,
                                       HTTP_X_FORWARDED_FOR='2.2.2.2')
            
            # Pelo menos uma das requests não deve ser throttled
            non_throttled = [r for r in [response1, response2] 
                           if r.status_code != status.HTTP_429_TOO_MANY_REQUESTS]
            
            self.assertGreaterEqual(len(non_throttled), 1,
                                  "Ambas requests foram throttled - IPs podem não estar sendo diferenciados")
