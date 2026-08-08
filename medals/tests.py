from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from categories.models import Category
from users.models import User, Role, Permission, UserRole, RolePermission
from users.permission_catalog import PERMISSIONS, DEFAULT_ROLES, ROLE_CURATOR, ROLE_VIEWER

from .models import Medal


def seed_catalog():
    perm_map = {}
    for codename, name, description in PERMISSIONS:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': name, 'description': description},
        )
        perm_map[codename] = perm
    roles = {}
    for codename, meta in DEFAULT_ROLES.items():
        role, _ = Role.objects.get_or_create(
            codename=codename,
            defaults={
                'name': meta['name'],
                'description': meta['description'],
                'is_active': True,
            },
        )
        for pcode in meta['permissions']:
            RolePermission.objects.get_or_create(role=role, permission=perm_map[pcode])
        roles[codename] = role
    return roles


class MedalAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(username='root', password='RootPass123!')
        self.curator = User.objects.create_user(username='curator', password='CuratorPass1!', is_active=True)
        UserRole.objects.create(user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser)
        self.viewer = User.objects.create_user(username='viewer', password='ViewerPass1!', is_active=True)
        UserRole.objects.create(user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser)
        self.plain = User.objects.create_user(username='plain', password='PlainPass123!', is_active=True)
        self.category = Category.objects.create(name='Military', slug='military')
        self.list_url = reverse('medals:medal-list')

    def _payload(self, **overrides):
        data = {
            'name': 'Order of the Lion',
            'country': 'Iran',
            'year': 1925,
            'category': self.category.pk,
            'weight': '25.500',
            'diameter': '40.00',
            'quality': 'XF',
            'authenticity': 'authentic',
            'purchase_price': '100.00',
            'purchase_currency': 'USD',
            'current_value': '150.00',
        }
        data.update(overrides)
        return data

    def test_unauthenticated_401(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_permission_403(self):
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_can_list_not_create(self):
        Medal.objects.create(name='Sample', country='Iran')
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        resp = self.client.post(self.list_url, self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_curator_crud(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        medal_id = resp.data['id']
        self.assertEqual(resp.data['name'], 'Order of the Lion')
        self.assertIn('category_detail', resp.data)

        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        detail = reverse('medals:medal-detail', kwargs={'pk': medal_id})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.patch(detail, {'notes': 'Restored'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['notes'], 'Restored')

        resp = self.client.delete(detail)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_can_create(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.post(self.list_url, self._payload(name='Royal Medal'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_negative_weight_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(weight='-1'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_price_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(purchase_price='-10'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_year_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(year=5000), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_name_required(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(name=''), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination(self):
        self.client.force_authenticate(user=self.viewer)
        for i in range(25):
            Medal.objects.create(name=f'Medal {i}')
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertIn('count', resp.data)
        self.assertLessEqual(len(resp.data['results']), 20)

    def test_list_select_related_no_error(self):
        Medal.objects.create(name='With Cat', category=self.category)
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = next(r for r in resp.data['results'] if r['name'] == 'With Cat')
        self.assertIsNotNone(item.get('category_detail'))
        self.assertEqual(item['category_detail']['name'], 'Military')
