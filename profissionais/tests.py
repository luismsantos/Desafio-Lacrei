# tests.py para o app profissionais

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Profissional


class ProfissionalModelTest(TestCase):
    """Testes para o model Profissional"""
    
    def setUp(self):
        """Dados de teste"""
        self.profissional_data = {
            'nome': 'João Silva',
            'especialidade': 'Psicologia',
            'email': 'joao@teste.com',
            'telefone': '(11)99999-9999'
        }
    
    def test_criar_profissional(self):
        """Testa criação de profissional"""
        profissional = Profissional.objects.create(**self.profissional_data)
        self.assertEqual(profissional.nome, 'João Silva')
        self.assertEqual(profissional.especialidade, 'Psicologia')
        self.assertEqual(profissional.email, 'joao@teste.com')
        self.assertIsNone(profissional.nome_social)
    
    def test_str_method(self):
        """Testa representação string do profissional"""
        profissional = Profissional.objects.create(**self.profissional_data)
        self.assertEqual(str(profissional), 'João Silva')
    
    def test_profissional_com_nome_social(self):
        """Testa profissional com nome social"""
        data_com_nome_social = self.profissional_data.copy()
        data_com_nome_social['nome_social'] = 'Joana'
        profissional = Profissional.objects.create(**data_com_nome_social)
        self.assertEqual(profissional.nome_social, 'Joana')


class ProfissionalAPITest(APITestCase):
    """Testes para API de profissionais"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.profissional_data = {
            'nome': 'Maria Santos',
            'especialidade': 'Clínica Geral',
            'email': 'maria@teste.com',
            'telefone': '(21)88888-8888'
        }
        
        # Cria profissional para testes de atualização/deleção
        self.profissional = Profissional.objects.create(**self.profissional_data)
        
        # URLs dos endpoints
        self.list_url = reverse('profissional-list')
        self.detail_url = reverse('profissional-detail', kwargs={'pk': self.profissional.pk})
    
    def test_listar_profissionais(self):
        """Testa listagem de profissionais"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_listar_profissionais_vazio(self):
        """Testa listagem quando não há profissionais"""
        Profissional.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_criar_profissional(self):
        """Testa criação de novo profissional via API"""
        data = {
            'nome': 'Ana Costa',
            'especialidade': 'Dermatologia',
            'email': 'ana@teste.com',
            'telefone': '(31)77777-7777'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2)
        self.assertEqual(response.data['nome'], 'Ana Costa')
    
    def test_criar_profissional_com_nome_social(self):
        """Testa criação de profissional com nome social"""
        data = {
            'nome': 'Carlos Oliveira',
            'nome_social': 'Carla',
            'especialidade': 'Psiquiatria',
            'email': 'carlos@teste.com',
            'telefone': '(41)66666-6666'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome_social'], 'Carla')
        self.assertEqual(response.data['nome_exibicao'], 'Carla')
    
    def test_nome_exibicao_sem_nome_social(self):
        """Testa campo nome_exibicao quando não há nome social"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_exibicao'], response.data['nome'])
    
    def test_buscar_profissional_por_id(self):
        """Testa busca de profissional específico"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Maria Santos')
    
    def test_buscar_profissional_inexistente(self):
        """Testa busca por profissional que não existe"""
        url_inexistente = reverse('profissional-detail', kwargs={'pk': 999})
        response = self.client.get(url_inexistente)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_atualizar_profissional(self):
        """Testa atualização de profissional"""
        data = {
            'nome': 'Maria Santos Silva',
            'especialidade': 'Pediatria',
            'email': 'maria.silva@teste.com',
            'telefone': '(21)99999-9999'
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="PATCH deveria atualizar com sucesso")
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.nome, 'Maria Santos Silva')
        self.assertEqual(self.profissional.especialidade, 'Pediatria')
    
    def test_atualizar_parcial_profissional(self):
        """Testa atualização parcial (PATCH)"""
        data = {'especialidade': 'Cardiologia'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.especialidade, 'Cardiologia')
        self.assertEqual(self.profissional.nome, 'Maria Santos')  # Nome não mudou
    
    def test_deletar_profissional(self):
        """Testa deleção de profissional"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)
    
    def test_criar_profissional_email_invalido(self):
        """Testa criação com email inválido"""
        data = self.profissional_data.copy()
        data['email'] = 'email-invalido'
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_criar_profissional_campos_obrigatorios(self):
        """Testa criação sem campos obrigatórios"""
        data = {'nome': 'Apenas Nome'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_email_unico(self):
        """Testa que email deve ser único"""
        # Tenta criar outro profissional com mesmo email
        data = self.profissional_data.copy()
        data['nome'] = 'Outro Nome'
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)