from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, Role, Permission, UserRole, RolePermission
from users.permission_catalog import PERMISSIONS, DEFAULT_ROLES, ROLE_CURATOR, ROLE_VIEWER

from .models import Category


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


class CategoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(username='root', password='RootPass123!')
        self.curator = User.objects.create_user(username='curator', password='CuratorPass1!', is_active=True)
        UserRole.objects.create(user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser)
        self.viewer = User.objects.create_user(username='viewer', password='ViewerPass1!', is_active=True)
        UserRole.objects.create(user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser)
        self.plain = User.objects.create_user(username='plain', password='PlainPass123!', is_active=True)
        self.list_url = reverse('categories:category-list')

    def test_unauthenticated_401(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_without_permission_403(self):
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_can_list_not_create(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        resp = self.client.post(self.list_url, {'name': 'War'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_curator_crud(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, {
            'name': 'Military',
            'description': 'Military medals',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cat_id = resp.data['id']
        self.assertTrue(resp.data['slug'])

        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)

        detail = reverse('categories:category-detail', kwargs={'pk': cat_id})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.patch(detail, {'description': 'Updated'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['description'], 'Updated')

        resp = self.client.delete(detail)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_delete(self):
        cat = Category.objects.create(name='Temp', slug='temp')
        self.client.force_authenticate(user=self.superuser)
        detail = reverse('categories:category-detail', kwargs={'pk': cat.pk})
        resp = self.client.delete(detail)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_duplicate_name_rejected(self):
        Category.objects.create(name='Sports', slug='sports')
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, {'name': 'sports'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_auto_generated(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, {'name': 'Royal Orders'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['slug'], 'royal-orders')
