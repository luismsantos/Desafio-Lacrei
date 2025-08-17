from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from profissionais.models import Profissional
from .models import Consulta
from datetime import timedelta
from authentication.test_mixins import AuthenticatedTestMixin

class ConsultaAPITest(AuthenticatedTestMixin, APITestCase):
    """Testes para API de consultas"""

    def setUp(self):
        # Cria profissional de referência
        self.prof = Profissional.objects.create(
            nome='Teste Prof',
            especialidade='Teste',
            email='prof@teste.com',
            telefone='(11)11111-1111'
        )

        # Urls
        self.list_url = reverse('consulta-list')

        # Cria uma consulta existente para detalhes
        self.consulta = Consulta.objects.create(
            profissional=self.prof,
            paciente_nome='Paciente A',
            data_hora='2025-08-16T10:00:00Z',
            observacoes='Sem observações'
        )
        self.detail_url = reverse('consulta-detail', kwargs={'pk': self.consulta.pk})

    def test_listar_consultas(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_listar_consultas_vazio(self):
        Consulta.objects.all().delete()
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_filtrar_consultas_por_profissional(self):
        # Cria outra consulta de outro prof
        outro = Profissional.objects.create(
            nome='Outro Prof',
            especialidade='Teste2',
            email='outro@teste.com',
            telefone='(22)22222-2222'
        )
        Consulta.objects.create(
            profissional=outro,
            paciente_nome='Paciente B',
            data_hora='2025-08-17T11:00:00Z',
            observacoes=''
        )
        resp = self.client.get(f"{self.list_url}?profissional_id={self.prof.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['paciente_nome'], 'Paciente A')

    def test_detalhe_consulta(self):
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['paciente_nome'], 'Paciente A')

    def test_buscar_consulta_inexistente(self):
        url = reverse('consulta-detail', kwargs={'pk': 999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_criar_consulta(self):
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,  
            'paciente_nome': 'Paciente C',
            'data_hora': (timezone.now() + timedelta(minutes=10)).isoformat(),
            'observacoes': 'Teste obs'
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_atualizar_consulta(self):
        self.authenticate_user()
        data = {'observacoes': 'Atualizado'}
        resp = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.observacoes, 'Atualizado')

    def test_deletar_consulta(self):
        self.authenticate_user()
        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)

    def test_campos_obrigatorios(self):
        self.authenticate_user()
        resp = self.client.post(self.list_url, {'profissional': self.prof.pk}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_paciente_nome_vazio(self):
        """Testa que nome do paciente não pode estar vazio"""
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,
            'paciente_nome': '   ',  # Apenas espaços
            'data_hora': (timezone.now() + timedelta(minutes=10)).isoformat(),
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('paciente_nome', resp.data)

    def test_paciente_nome_apenas_espacos(self):
        """Testa que nome do paciente não pode ser apenas espaços"""
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,
            'paciente_nome': '',  # String vazia
            'data_hora': (timezone.now() + timedelta(minutes=10)).isoformat(),
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('paciente_nome', resp.data)

    def test_data_no_passado(self):
        """Testa que não é possível criar consulta no passado"""
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,
            'paciente_nome': 'Paciente Teste',
            'data_hora': (timezone.now() - timedelta(hours=1)).isoformat(),
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('data_hora', resp.data)

    def test_observacoes_vazias_string(self):
        """Testa que observações não podem ser string vazia com espaços"""
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,
            'paciente_nome': 'Paciente Teste',
            'data_hora': (timezone.now() + timedelta(minutes=10)).isoformat(),
            'observacoes': '   '  # Apenas espaços
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('observacoes', resp.data)

    def test_observacoes_none_valido(self):
        """Testa que observações podem ser None ou não informadas"""
        self.authenticate_user()
        data = {
            'profissional_id': self.prof.pk,
            'paciente_nome': 'Paciente Teste',
            'data_hora': (timezone.now() + timedelta(minutes=10)).isoformat(),
        }
        resp = self.client.post(self.list_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)