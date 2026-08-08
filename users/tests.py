"""
API and RBAC tests for the users app.
Run: python manage.py test users
"""
from django.test import TestCase, override_settings
from django.urls import reverse, clear_url_caches
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role, Permission, UserRole, RolePermission
from .permissions import SYSTEM_ADMIN_ROLE_CODENAME
from .permission_catalog import PERMISSIONS, DEFAULT_ROLES, ROLE_ADMIN, ROLE_CURATOR, ROLE_VIEWER


def seed_catalog():
    perm_map = {}
    for codename, name, description in PERMISSIONS:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={"name": name, "description": description},
        )
        perm_map[codename] = perm
    roles = {}
    for codename, meta in DEFAULT_ROLES.items():
        role, _ = Role.objects.get_or_create(
            codename=codename,
            defaults={
                "name": meta["name"],
                "description": meta["description"],
                "is_active": True,
            },
        )
        for pcode in meta["permissions"]:
            RolePermission.objects.get_or_create(role=role, permission=perm_map[pcode])
        roles[codename] = role
    return roles, perm_map


class UsersAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles, self.perms = seed_catalog()
        self.admin = User.objects.create_superuser(username="admin", password="AdminPass123!")
        self.role_admin = self.roles[ROLE_ADMIN]
        self.role_viewer = self.roles[ROLE_VIEWER]
        self.plain = User.objects.create_user(username="plain", password="PlainPass123!", is_active=True)
        self.role_admin_user = User.objects.create_user(username="roleadmin", password="RoleAdmin1!", is_active=True)
        UserRole.objects.create(user=self.role_admin_user, role=self.role_admin, assigned_by=self.admin)

    def test_login_success(self):
        resp = self.client.post(reverse("users:login"), {"username": "admin", "password": "AdminPass123!"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertNotIn("last_login_ip", resp.data["user"])

    def test_login_case_insensitive_username(self):
        resp = self.client.post(reverse("users:login"), {"username": "ADMIN", "password": "AdminPass123!"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_login_unknown_username(self):
        resp = self.client.post(reverse("users:login"), {"username": "nosuch", "password": "Whatever12!"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse("users:me")).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_permission_gated(self):
        url = reverse("users:user-list")
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.role_admin_user)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_invite_create_and_consume(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(reverse("users:invite-create"), {
            "username": "newbie", "password": "NewbiePass12!", "expires_in_hours": 24,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        token = resp.data["token"]
        self.client.force_authenticate(user=None)
        resp = self.client.post(reverse("users:invite-consume", kwargs={"token": token}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(username="newbie").is_active)

    def test_logout_own_refresh_token(self):
        refresh = RefreshToken.for_user(self.plain)
        self.client.force_authenticate(user=self.plain)
        resp = self.client.post(reverse("users:logout"), {"refresh": str(refresh)}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_other_user_refresh_token_rejected(self):
        other = RefreshToken.for_user(self.admin)
        self.client.force_authenticate(user=self.plain)
        resp = self.client.post(reverse("users:logout"), {"refresh": str(other)}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_admin_cannot_grant_admin_role(self):
        target = User.objects.create_user(username="t1", password="TargetPass12!", is_active=True)
        self.client.force_authenticate(user=self.role_admin_user)
        resp = self.client.put(reverse("users:user-roles", kwargs={"pk": target.pk}), {"role_ids": [self.role_admin.pk]}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_superuser_can_grant_admin_role(self):
        target = User.objects.create_user(username="t2", password="TargetPass12!", is_active=True)
        self.client.force_authenticate(user=self.admin)
        resp = self.client.put(reverse("users:user-roles", kwargs={"pk": target.pk}), {"role_ids": [self.role_admin.pk]}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(target.has_role(SYSTEM_ADMIN_ROLE_CODENAME))

    def test_admin_system_role_cannot_be_deleted(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.delete(reverse("users:role-detail", kwargs={"pk": self.role_admin.pk}))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RBACPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles, self.perms = seed_catalog()
        self.superuser = User.objects.create_superuser(username="root", password="RootPass123!")
        self.admin_user = User.objects.create_user(username="adminuser", password="AdminUser1!", is_active=True)
        UserRole.objects.create(user=self.admin_user, role=self.roles[ROLE_ADMIN], assigned_by=self.superuser)
        self.curator = User.objects.create_user(username="curator", password="CuratorPass1!", is_active=True)
        UserRole.objects.create(user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser)
        self.viewer = User.objects.create_user(username="viewer", password="ViewerPass1!", is_active=True)
        UserRole.objects.create(user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser)

    def test_superuser_can_access_user_list(self):
        self.client.force_authenticate(user=self.superuser)
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_200_OK)

    def test_admin_has_users_view_and_invite(self):
        self.client.force_authenticate(user=self.admin_user)
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_200_OK)
        resp = self.client.post(reverse("users:invite-create"), {
            "username": "inv1", "password": "InvitedPass1!", "expires_in_hours": 12,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_curator_denied_user_management(self):
        self.client.force_authenticate(user=self.curator)
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(reverse("users:role-list")).status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_denied_mutations(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_403_FORBIDDEN)

    def test_curator_has_medals_permissions_in_resolution(self):
        self.assertTrue(self.curator.has_custom_perm("medals.view"))
        self.assertTrue(self.curator.has_custom_perm("medals.create"))
        self.assertFalse(self.curator.has_custom_perm("users.delete"))

    def test_viewer_read_only_resolution(self):
        self.assertTrue(self.viewer.has_custom_perm("medals.view"))
        self.assertFalse(self.viewer.has_custom_perm("medals.create"))
        self.assertTrue(self.viewer.has_custom_perm("reports.view"))

    def test_multi_role_union(self):
        UserRole.objects.create(user=self.viewer, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser)
        self.viewer.clear_permission_cache()
        self.assertTrue(self.viewer.has_custom_perm("medals.create"))

    def test_inactive_role_denied(self):
        role = self.roles[ROLE_CURATOR]
        role.is_active = False
        role.save(update_fields=["is_active"])
        self.curator.clear_permission_cache()
        self.assertFalse(self.curator.has_custom_perm("medals.view"))

    def test_permission_removal_revokes_access(self):
        RolePermission.objects.filter(role=self.roles[ROLE_ADMIN], permission__codename="users.view").delete()
        self.admin_user.clear_permission_cache()
        self.client.force_authenticate(user=self.admin_user)
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_401(self):
        self.assertEqual(self.client.get(reverse("users:user-list")).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_bypasses_without_roles(self):
        bare = User.objects.create_superuser(username="bare", password="BarePass123!")
        self.assertTrue(bare.has_custom_perm("users.delete"))

    def test_admin_role_matrix_contains_management_perms(self):
        codes = self.admin_user.get_permission_codenames()
        for required in ("users.view", "users.create", "roles.assign", "permissions.view"):
            self.assertIn(required, codes)
