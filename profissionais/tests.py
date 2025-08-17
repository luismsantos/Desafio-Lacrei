# tests.py para o app profissionais

from rest_framework import status
from rest_framework.test import APITestCase

from django.test import TestCase
from django.urls import reverse

from authentication.test_mixins import AuthenticatedTestMixin

from .models import Profissional


class ProfissionalModelTest(TestCase):
    """Testes para o model Profissional"""

    def setUp(self):
        """Dados de teste"""
        self.profissional_data = {
            "nome": "João Silva",
            "especialidade": "Psicologia",
            "email": "joao@teste.com",
            "telefone": "(11)99999-9999",
        }

    def test_criar_profissional(self):
        """Testa criação de profissional"""
        profissional = Profissional.objects.create(**self.profissional_data)
        self.assertEqual(profissional.nome, "João Silva")
        self.assertEqual(profissional.especialidade, "Psicologia")
        self.assertEqual(profissional.email, "joao@teste.com")
        self.assertIsNone(profissional.nome_social)

    def test_str_method(self):
        """Testa representação string do profissional"""
        profissional = Profissional.objects.create(**self.profissional_data)
        self.assertEqual(str(profissional), "João Silva")

    def test_profissional_com_nome_social(self):
        """Testa profissional com nome social"""
        data_com_nome_social = self.profissional_data.copy()
        data_com_nome_social["nome_social"] = "Joana"
        profissional = Profissional.objects.create(**data_com_nome_social)
        self.assertEqual(profissional.nome_social, "Joana")


class ProfissionalAPITest(AuthenticatedTestMixin, APITestCase):
    """Testes para API de profissionais"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.profissional_data = {
            "nome": "Maria Santos",
            "especialidade": "Clínica Geral",
            "email": "maria@teste.com",
            "telefone": "(21)88888-8888",
        }

        self.profissional = Profissional.objects.create(**self.profissional_data)

        self.list_url = reverse("profissional-list")
        self.detail_url = reverse(
            "profissional-detail", kwargs={"pk": self.profissional.pk}
        )

    def test_listar_profissionais(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_listar_profissionais_vazio(self):
        Profissional.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_criar_profissional(self):
        self.authenticate_user()
        data = {
            "nome": "Ana Costa",
            "especialidade": "Dermatologia",
            "email": "ana@teste.com",
            "telefone": "(31)77777-7777",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2)
        self.assertEqual(response.data["nome"], "Ana Costa")

    def test_criar_profissional_com_nome_social(self):
        self.authenticate_user()
        data = {
            "nome": "Carlos Oliveira",
            "nome_social": "Carla",
            "especialidade": "Psiquiatria",
            "email": "carlos@teste.com",
            "telefone": "(41)66666-6666",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nome_social"], "Carla")
        self.assertEqual(response.data["nome_exibicao"], "Carla")

    def test_nome_exibicao_sem_nome_social(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome_exibicao"], response.data["nome"])

    def test_buscar_profissional_por_id(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Maria Santos")

    def test_buscar_profissional_inexistente(self):
        url_inexistente = reverse("profissional-detail", kwargs={"pk": 999})
        response = self.client.get(url_inexistente)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_atualizar_profissional(self):
        self.authenticate_user()
        data = {
            "nome": "Maria Santos Silva",
            "especialidade": "Pediatria",
            "email": "maria.silva@teste.com",
            "telefone": "(21)99999-9999",
        }
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.nome, "Maria Santos Silva")
        self.assertEqual(self.profissional.especialidade, "Pediatria")

    def test_atualizar_parcial_profissional(self):
        self.authenticate_user()
        data = {"especialidade": "Cardiologia"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.especialidade, "Cardiologia")
        self.assertEqual(self.profissional.nome, "Maria Santos")

    def test_deletar_profissional(self):
        self.authenticate_user()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)

    def test_criar_profissional_email_invalido(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["email"] = "email-invalido"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_profissional_campos_obrigatorios(self):
        self.authenticate_user()
        data = {"nome": "Apenas Nome"}
        # especialidade, email e telefone faltando
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_unico(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["nome"] = "Outro Nome"
        data["email"] = "maria@teste.com"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # validações extras

    def test_nome_vazio_espacos(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["nome"] = "   "
        data["email"] = "nomevazio@test.com"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nome", response.data)

    def test_especialidade_vazia(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["especialidade"] = "   "
        data["email"] = "especialidadevazia@test.com"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("especialidade", response.data)

    def test_telefone_invalido(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["telefone"] = "abc123"
        data["email"] = "telefoneinvalido@test.com"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("telefone", response.data)

    def test_nome_social_espacos(self):
        self.authenticate_user()
        data = self.profissional_data.copy()
        data["nome_social"] = "   "
        data["email"] = "nombresocial@test.com"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nome_social", response.data)
