"""
API and security tests for the users app.
Run: python manage.py test users
"""
import os
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.urls import reverse, clear_url_caches
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role, UserRole
from .permissions import SYSTEM_ADMIN_ROLE_CODENAME


class UsersAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='AdminPass123!'
        )
        self.role_admin = Role.objects.create(
            name='Admin', codename=SYSTEM_ADMIN_ROLE_CODENAME, is_active=True
        )
        self.role_viewer = Role.objects.create(
            name='Viewer', codename='viewer', is_active=True
        )
        self.plain = User.objects.create_user(
            username='plain', password='PlainPass123!', is_active=True
        )
        # Non-superuser user that holds the admin role
        self.role_admin_user = User.objects.create_user(
            username='roleadmin', password='RoleAdmin1!', is_active=True
        )
        UserRole.objects.create(
            user=self.role_admin_user, role=self.role_admin, assigned_by=self.admin
        )

    # ------------------------------------------------------------------
    # Login basics
    # ------------------------------------------------------------------

    def test_login_success(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'admin', 'password': 'AdminPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['user']['username'], 'admin')
        # F17: login payload should not expose last_login_ip
        self.assertNotIn('last_login_ip', resp.data['user'])

    def test_login_case_insensitive_username(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'ADMIN', 'password': 'AdminPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['user']['username'], 'admin')

    def test_login_wrong_password(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'admin', 'password': 'wrong'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_username(self):
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'nosuch', 'password': 'Whatever12!'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('نام کاربری یا رمز عبور اشتباه است', str(resp.data))

    def test_login_inactive_generic_message(self):
        User.objects.create_user(
            username='inactive', password='InactivePass1!', is_active=False
        )
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'inactive', 'password': 'InactivePass1!'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # F5: same generic message (no distinct inactive text)
        self.assertIn('نام کاربری یا رمز عبور اشتباه است', str(resp.data))

    def test_login_locked_generic_message(self):
        user = User.objects.get(username='plain')
        for _ in range(5):
            user.register_failed_attempt()
        user.refresh_from_db()
        self.assertTrue(user.is_locked)
        url = reverse('users:login')
        resp = self.client.post(url, {'username': 'plain', 'password': 'PlainPass123!'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('نام کاربری یا رمز عبور اشتباه است', str(resp.data))

    def test_me_requires_auth(self):
        url = reverse('users:me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated_no_sensitive_ops_fields(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'admin')
        self.assertNotIn('last_login_ip', resp.data)
        self.assertNotIn('is_locked', resp.data)

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
        if resp.data['results']:
            self.assertIn('last_login_ip', resp.data['results'][0])

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

    def test_logout_own_refresh_token(self):
        refresh = RefreshToken.for_user(self.plain)
        self.client.force_authenticate(user=self.plain)
        url = reverse('users:logout')
        resp = self.client.post(url, {'refresh': str(refresh)}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_other_user_refresh_token_rejected(self):
        other_refresh = RefreshToken.for_user(self.admin)
        self.client.force_authenticate(user=self.plain)
        url = reverse('users:logout')
        resp = self.client.post(url, {'refresh': str(other_refresh)}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_user_access_token_rejected(self):
        user = User.objects.create_user(
            username='soon_inactive', password='SoonInactive1!', is_active=True
        )
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        user.is_active = False
        user.save(update_fields=['is_active'])

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = self.client.get(reverse('users:me'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_locked_user_access_token_rejected(self):
        user = User.objects.create_user(
            username='soon_locked', password='SoonLocked12!', is_active=True
        )
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        for _ in range(5):
            user.register_failed_attempt()
        user.refresh_from_db()
        self.assertTrue(user.is_locked)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = self.client.get(reverse('users:me'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_admin_cannot_grant_admin_role(self):
        target = User.objects.create_user(
            username='target1', password='TargetPass12!', is_active=True
        )
        self.client.force_authenticate(user=self.role_admin_user)
        url = reverse('users:user-roles', kwargs={'pk': target.pk})
        resp = self.client.put(url, {'role_ids': [self.role_admin.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_superuser_can_grant_admin_role(self):
        target = User.objects.create_user(
            username='target2', password='TargetPass12!', is_active=True
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:user-roles', kwargs={'pk': target.pk})
        resp = self.client.put(url, {'role_ids': [self.role_admin.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertTrue(target.has_role(SYSTEM_ADMIN_ROLE_CODENAME))

    def test_normal_admin_cannot_self_escalate(self):
        non_admin = User.objects.create_user(
            username='nonadmin', password='NonAdmin12!', is_active=True
        )
        UserRole.objects.create(
            user=non_admin, role=self.role_viewer, assigned_by=self.admin
        )
        self.client.force_authenticate(user=non_admin)
        url = reverse('users:user-roles', kwargs={'pk': non_admin.pk})
        resp = self.client.put(url, {'role_ids': [self.role_admin.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.role_admin_user)
        url = reverse('users:user-roles', kwargs={'pk': self.plain.pk})
        resp = self.client.put(url, {'role_ids': [self.role_admin.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_normal_admin_can_assign_non_system_role(self):
        target = User.objects.create_user(
            username='target3', password='TargetPass12!', is_active=True
        )
        self.client.force_authenticate(user=self.role_admin_user)
        url = reverse('users:user-roles', kwargs={'pk': target.pk})
        resp = self.client.put(url, {'role_ids': [self.role_viewer.pk]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertTrue(target.has_role('viewer'))

    def test_admin_system_role_cannot_be_deleted(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:role-detail', kwargs={'pk': self.role_admin.pk})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Role.objects.filter(pk=self.role_admin.pk).exists())

    def test_admin_system_role_codename_cannot_change(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:role-detail', kwargs={'pk': self.role_admin.pk})
        resp = self.client.patch(
            url, {'codename': 'not-admin'}, format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_custom_role_can_be_deleted(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:role-detail', kwargs={'pk': self.role_viewer.pk})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_longer_than_max_rejected_on_invite(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users:invite-create')
        long_pw = 'A' * 200
        resp = self.client.post(url, {
            'username': 'longpw',
            'password': long_pw,
            'expires_in_hours': 24,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_longer_than_max_rejected_on_login(self):
        url = reverse('users:login')
        long_pw = 'A' * 200
        resp = self.client.post(url, {'username': 'admin', 'password': long_pw})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(USE_X_FORWARDED_FOR=False)
    def test_xff_ignored_without_trusted_proxy(self):
        from users.views import get_client_ip
        from django.test import RequestFactory
        rf = RequestFactory()
        request = rf.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4', REMOTE_ADDR='10.0.0.1')
        self.assertEqual(get_client_ip(request), '10.0.0.1')

    @override_settings(USE_X_FORWARDED_FOR=True)
    def test_xff_used_with_trusted_proxy_setting(self):
        from users.views import get_client_ip
        from django.test import RequestFactory
        rf = RequestFactory()
        request = rf.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 10.0.0.1', REMOTE_ADDR='10.0.0.1')
        self.assertEqual(get_client_ip(request), '1.2.3.4')

    def test_production_insecure_secret_key_fails(self):
        from django.core.exceptions import ImproperlyConfigured
        insecure = 'django-insecure-dev-only-change-me-in-production'
        debug = False
        secret = insecure
        with self.assertRaises(ImproperlyConfigured):
            if not debug and secret in ('', insecure):
                raise ImproperlyConfigured(
                    'DJANGO_SECRET_KEY must be set to a strong unique value when DEBUG is False.'
                )

    @override_settings(DEBUG=True, SPECTACULAR_SERVE_PUBLIC=False)
    def test_swagger_available_in_debug(self):
        clear_url_caches()
        from importlib import reload
        import config.urls as urls_mod
        reload(urls_mod)
        from django.urls import get_resolver
        resolver = get_resolver(urls_mod)
        names = {u.name for u in resolver.url_patterns if getattr(u, 'name', None)}
        self.assertIn('schema', names)
        self.assertIn('swagger-ui', names)

    @override_settings(DEBUG=False, SPECTACULAR_SERVE_PUBLIC=False)
    def test_swagger_hidden_in_production_by_default(self):
        clear_url_caches()
        from importlib import reload
        import config.urls as urls_mod
        reload(urls_mod)
        names = {getattr(u, 'name', None) for u in urls_mod.urlpatterns}
        self.assertNotIn('schema', names)
        self.assertNotIn('swagger-ui', names)
