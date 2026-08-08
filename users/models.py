import hashlib
import secrets

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class Permission(models.Model):
    """
    Application-level permission, independent of django.contrib.auth.Permission.
    Example: medals.create, users.view
    """
    codename = models.SlugField(max_length=100, unique=True, verbose_name='کدنام')
    name = models.CharField(max_length=150, verbose_name='نام')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        ordering = ['codename']
        verbose_name = 'مجوز'
        verbose_name_plural = 'مجوزها'

    def __str__(self):
        return self.codename


class Role(models.Model):
    """System roles (ACL) - e.g. admin, curator, viewer"""
    name = models.CharField(max_length=50, unique=True, verbose_name='نام نقش')
    codename = models.SlugField(max_length=50, unique=True, verbose_name='کدنام')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    permissions = models.ManyToManyField(
        Permission, through='RolePermission', related_name='roles', blank=True,
        verbose_name='مجوزها'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        ordering = ['name']
        verbose_name = 'نقش'
        verbose_name_plural = 'نقش‌ها'

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name='role_permission_set',
        verbose_name='نقش'
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name='permission_role_set',
        verbose_name='مجوز'
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ اعطا')

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = 'مجوز نقش'
        verbose_name_plural = 'مجوزهای نقش'

    def __str__(self):
        return f'{self.role} -> {self.permission}'


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user. No public registration path;
    users are created only by admin via InviteLink.
    """
    username = models.CharField(
        max_length=150, unique=True, db_index=True, verbose_name='نام کاربری'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')
    first_name = models.CharField(max_length=100, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=100, blank=True, verbose_name='نام خانوادگی')

    roles = models.ManyToManyField(
        Role, through='UserRole', through_fields=('user', 'role'),
        related_name='users', blank=True, verbose_name='نقش‌ها'
    )

    is_active = models.BooleanField(
        default=False, verbose_name='فعال'
    )
    is_staff = models.BooleanField(
        default=False, verbose_name='دسترسی پنل جنگو'
    )

    must_change_password = models.BooleanField(
        default=False, verbose_name='باید رمز عبور را تغییر دهد'
    )

    failed_login_attempts = models.PositiveIntegerField(
        default=0, verbose_name='تعداد تلاش‌های ناموفق ورود'
    )
    locked_until = models.DateTimeField(
        null=True, blank=True, verbose_name='قفل تا تاریخ'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True, blank=True, verbose_name='آی‌پی آخرین ورود'
    )

    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='created_users', verbose_name='ساخته‌شده توسط'
    )

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())

    def register_failed_attempt(self, max_attempts=5, lock_minutes=15):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lock_minutes)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_attempts(self):
        if self.failed_login_attempts or self.locked_until:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def get_permission_codenames(self) -> set:
        """
        Efficient resolution of effective application permission codenames.

        - Superuser: has_custom_perm short-circuits; no full Permission load.
        - Non-superuser: one query joining active roles via UserRole → Role → Permission.
        - Result is cached on the instance for the lifetime of the request/object.
        """
        cached = getattr(self, '_permission_codenames_cache', None)
        if cached is not None:
            return cached

        if self.is_superuser:
            result = set()
            self._permission_codenames_cache = result
            return result

        result = set(
            Permission.objects.filter(
                roles__is_active=True,
                roles__user_role_set__user_id=self.pk,
            )
            .values_list('codename', flat=True)
            .distinct()
        )
        self._permission_codenames_cache = result
        return result

    def clear_permission_cache(self) -> None:
        """Invalidate cached permission set after role changes."""
        if hasattr(self, '_permission_codenames_cache'):
            del self._permission_codenames_cache

    def has_custom_perm(self, codename: str) -> bool:
        if not self.is_authenticated:
            return False
        if self.is_superuser:
            return True
        return codename in self.get_permission_codenames()

    def has_role(self, codename: str) -> bool:
        return self.roles.filter(codename=codename, is_active=True).exists()


class UserRole(models.Model):
    """Through table for role assignment audit trail."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_role_set',
        verbose_name='کاربر'
    )
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name='user_role_set',
        verbose_name='نقش'
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles',
        verbose_name='تخصیص‌دهنده'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تخصیص')

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'نقش کاربر'
        verbose_name_plural = 'نقش‌های کاربران'

    def __str__(self):
        return f'{self.user} -> {self.role}'


def generate_raw_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


class InviteLink(models.Model):
    """
    One-time invite link. Raw token is never stored; only SHA-256 hash.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='invite_link',
        verbose_name='کاربر'
    )
    token_hash = models.CharField(
        max_length=64, unique=True, db_index=True, verbose_name='هش توکن'
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_invites',
        verbose_name='ساخته‌شده توسط'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    expires_at = models.DateTimeField(verbose_name='تاریخ انقضا')

    is_used = models.BooleanField(default=False, verbose_name='مصرف‌شده')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ مصرف')
    used_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='آی‌پی مصرف‌کننده')
    created_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='آی‌پی سازنده')

    class Meta:
        verbose_name = 'لینک دعوت یک‌بار مصرف'
        verbose_name_plural = 'لینک‌های دعوت'
        ordering = ['-created_at']

    def __str__(self):
        status = 'مصرف‌شده' if self.is_used else 'فعال'
        return f'Invite({self.user.username}) - {status}'

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return (not self.is_used) and (not self.is_expired)
