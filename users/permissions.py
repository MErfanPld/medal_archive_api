from rest_framework.permissions import BasePermission


# Codename of the built-in system administrator role (F2 / F19).
SYSTEM_ADMIN_ROLE_CODENAME = 'admin'
SYSTEM_ROLE_CODENAMES = frozenset({SYSTEM_ADMIN_ROLE_CODENAME})


class IsAdminRole(BasePermission):
    """فقط کاربرانی که نقش admin دارند یا سوپریوزر هستند"""
    message = 'شما دسترسی ادمین ندارید.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return bool(user.is_superuser or user.has_role(SYSTEM_ADMIN_ROLE_CODENAME))


class HasCustomPermission(BasePermission):
    """
    Permission پارامتری بر اساس مجوز اپلیکیشنی (ACL).
    استفاده:
        permission_classes = [IsAuthenticated, require_permission('user.invite.create')]
    """
    message = 'شما مجوز لازم برای این عملیات را ندارید.'

    def __init__(self, codename: str):
        self.codename = codename

    def __call__(self):
        # DRF نمونه‌ی کلاس permission را با فراخوانی () می‌سازد؛
        # چون خودمان از قبل نمونه ساخته‌ایم، خودش را برمی‌گردانیم.
        return self

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.has_custom_perm(self.codename)


def require_permission(codename: str) -> HasCustomPermission:
    """هلپر برای استفاده راحت در permission_classes"""
    return HasCustomPermission(codename)
