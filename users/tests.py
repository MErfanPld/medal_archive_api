"""
Basic API tests for the users app.
Run: python manage.py test users
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import User, Role


class UsersAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='AdminPass123!'
        )
        self.role_admin = Role.objects.create(
            name='Admin', codename='admin', is_active=True
        )
        self.plain = User.objects.create_user(
            username='plain', password='PlainPass123!', is_active=True
        )

    def test_login_success(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'admin', 'password': 'AdminPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['user']['username'], 'admin')

    def test_login_case_insensitive_username(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'ADMIN', 'password': 'AdminPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['user']['username'], 'admin')

    def test_login_wrong_password(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'admin', 'password': 'wrong'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive(self):
        User.objects.create_user(
            username='inactive', password='InactivePass1!', is_active=False
        )
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'inactive', 'password': 'InactivePass1!'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_requires_auth(self):
        url = reverse('users:me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'admin')

    def test_user_list_admin_only(self):
        url = reverse('users:user-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.plain)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)

    def test_invite_create_and_consume(self):
        self.client.force_authenticate(user=self.admin)
        create_url = reverse('users:invite-create')
        resp = self.client.post(create_url, {
            'username': 'newbie',
            'password': 'NewbiePass12!',
            'email': 'newbie@example.com',
            'expires_in_hours': 24,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        token = resp.data['token']
        self.assertTrue(token)
        user = User.objects.get(username='newbie')
        self.assertFalse(user.is_active)

        self.client.force_authenticate(user=None)
        consume_url = reverse('users:invite-consume', kwargs={'token': token})
        resp = self.client.post(consume_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        resp = self.client.post(consume_url)
        self.assertEqual(resp.status_code, status.HTTP_410_GONE)

    def test_lockout_after_failed_attempts(self):
        # Exercise model lockout directly to avoid login throttle (5/min)
        user = User.objects.get(username='plain')
        for _ in range(5):
            user.register_failed_attempt()
        user.refresh_from_db()
        self.assertTrue(user.is_locked)
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'plain', 'password': 'PlainPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('\u0642\u0641\u0644', str(resp.data))
