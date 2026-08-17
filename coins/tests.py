from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from categories.models import Category
from users.models import Permission, Role, User, UserRole
from users.permission_catalog import DEFAULT_ROLES, PERMISSIONS, ROLE_ADMIN, ROLE_VIEWER

from .models import Coin, ItemType


def seed_rbac():
    perms = {}
    for codename, name, description in PERMISSIONS:
        p, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': name, 'description': description},
        )
        perms[codename] = p
    roles = {}
    for codename, meta in DEFAULT_ROLES.items():
        role, _ = Role.objects.get_or_create(
            codename=codename,
            defaults={'name': meta['name'], 'description': meta['description'], 'is_active': True},
        )
        role.permissions.set([perms[c] for c in meta['permissions'] if c in perms])
        roles[codename] = role
    return roles, perms


class CoinAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles, self.perms = seed_rbac()
        self.superuser = User.objects.create_superuser(username='root', password='RootPass123!')
        self.admin = User.objects.create_user(username='adminu', password='AdminPass1!', is_active=True)
        UserRole.objects.create(user=self.admin, role=self.roles[ROLE_ADMIN], assigned_by=self.superuser)
        self.viewer = User.objects.create_user(username='viewer', password='ViewerPass1!', is_active=True)
        UserRole.objects.create(user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser)
        self.category = Category.objects.create(name='سکه‌های قاجار')
        self.list_url = reverse('coins:coin-list')

    def test_list_requires_auth(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_and_list(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'name': 'سکه طلای دو تومانی',
            'item_type': ItemType.COIN,
            'country': 'ایران',
            'year': 1925,
            'face_value': '2',
            'denomination': 'تومان',
            'material': 'طلا',
            'catalog_number': 'IR-COIN-1925-001',
            'category_id': self.category.id,
        }
        resp = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(Coin.objects.count(), 1)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.post(
            self.list_url,
            {'name': 'x', 'item_type': ItemType.COIN},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_item_type(self):
        Coin.objects.create(name='سکه ۱', item_type=ItemType.COIN, country='ایران')
        Coin.objects.create(name='اسکناس ۱', item_type=ItemType.BANKNOTE, country='ایران')
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.list_url, {'item_type': 'banknote'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get('results', resp.data)
        self.assertTrue(all(r['item_type'] == 'banknote' for r in results))
