"""
Application RBAC / fine-grained ACL for the REST API.

Permission resolution flows through User.has_custom_perm / get_permission_codenames.
Views declare either:
  - required_permission = "medals.view"
  - permission_map = {"list": "medals.view", "create": "medals.create", ...}

IsAdminRole remains as a bootstrap helper (role codename == admin OR superuser)
but protected management endpoints should prefer HasAppPermission + permission_map.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission


# Codename of the built-in system administrator role (bootstrap / escalation guard).
SYSTEM_ADMIN_ROLE_CODENAME = 'admin'
SYSTEM_ROLE_CODENAMES = frozenset({SYSTEM_ADMIN_ROLE_CODENAME})


class IsAdminRole(BasePermission):
    """
    Bootstrap check: superuser OR active role with codename 'admin'.

    Prefer HasAppPermission with explicit codenames for new endpoints.
    Kept for compatibility and endpoints that intentionally require the admin role.
    """

    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return bool(user.is_superuser or user.has_role(SYSTEM_ADMIN_ROLE_CODENAME))


class HasAppPermission(BasePermission):
    """
    Enforce application ACL using view.required_permission or view.permission_map.

    Usage on a generic APIView:
        permission_classes = [IsAuthenticated, HasAppPermission]
        required_permission = 'users.view'

    Usage on a ViewSet / ListCreateAPIView:
        permission_classes = [IsAuthenticated, HasAppPermission]
        permission_map = {
            'list': 'medals.view',
            'retrieve': 'medals.view',
            'create': 'medals.create',
            'update': 'medals.update',
            'partial_update': 'medals.update',
            'destroy': 'medals.delete',
        }

    Superuser always passes. Missing map entry for an action denies access.
    """

    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True

        codename = self._resolve_codename(request, view)
        if not codename:
            return False
        return user.has_custom_perm(codename)

    def has_object_permission(self, request, view, obj):
        # Default: same as view-level check. Object-level rules can override later.
        return self.has_permission(request, view)

    def _resolve_codename(self, request, view):
        permission_map = getattr(view, 'permission_map', None)
        if permission_map:
            action = getattr(view, 'action', None)
            if action is None:
                action = self._infer_action(request, view)
            return permission_map.get(action)

        required = getattr(view, 'required_permission', None)
        if required:
            return required
        return None

    @staticmethod
    def _infer_action(request, view):
        """Map HTTP method to a DRF-style action name for non-ViewSet class-based views."""
        method = request.method.lower()
        if method == 'get':
            lookup = getattr(view, 'lookup_url_kwarg', None) or getattr(view, 'lookup_field', 'pk')
            if lookup in getattr(view, 'kwargs', {}) or 'pk' in getattr(view, 'kwargs', {}):
                return 'retrieve'
            return 'list'
        return {
            'post': 'create',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }.get(method, method)


class HasCustomPermission(BasePermission):
    """
    Fixed-codename permission (legacy helper).

    Prefer HasAppPermission + required_permission / permission_map on the view.
    Still useful for one-off endpoints:
        permission_classes = [IsAuthenticated, require_permission('medals.create')]
    """

    message = 'You do not have permission to perform this action.'

    def __init__(self, codename=None):
        self.codename = codename

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if not self.codename:
            return False
        return user.has_custom_perm(self.codename)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def require_permission(codename):
    """Helper for permission_classes = [IsAuthenticated, require_permission('x.y')]."""
    return HasCustomPermission(codename)
