from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role, Permission, UserRole
from .permissions import SYSTEM_ADMIN_ROLE_CODENAME

# Precomputed dummy hash used only to normalize timing on unknown usernames (F6).
# Not tied to any real user row.
_DUMMY_PASSWORD_HASH = make_password('!unused-dummy-password-for-timing-only!')

_GENERIC_LOGIN_ERROR = 'نام کاربری یا رمز عبور اشتباه است.'

_PASSWORD_MAX_LENGTH = getattr(settings, 'PASSWORD_MAX_LENGTH', 128)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'description']
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, write_only=True,
        source='permissions', required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'codename', 'description', 'is_active', 'permissions', 'permission_ids']
        read_only_fields = ['id']

    def validate_codename(self, value):
        # F19: prevent renaming an existing system role's codename away from its identity
        # and prevent creating a second role that collides with system codenames via update.
        instance = getattr(self, 'instance', None)
        if instance is not None and instance.codename == SYSTEM_ADMIN_ROLE_CODENAME:
            if value != SYSTEM_ADMIN_ROLE_CODENAME:
                raise serializers.ValidationError(
                    'کدنام نقش سیستمی admin قابل تغییر نیست.'
                )
        return value

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        if permissions:
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        # F19: system admin role may have name/description/permissions updated,
        # but not codename (validated above) and not deletion (handled in the view).
        permissions = validated_data.pop('permissions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance


class RoleMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'codename']


class UserSerializer(serializers.ModelSerializer):
    """Admin-facing user representation (may include operational fields)."""
    roles = RoleMiniSerializer(many=True, read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'roles', 'is_active', 'is_locked', 'must_change_password',
            'date_joined', 'last_login', 'last_login_ip',
        ]
        read_only_fields = fields


class UserMeSerializer(serializers.ModelSerializer):
    """Self representation for /me/ and login payloads — omits operational IP."""
    roles = RoleMiniSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'roles', 'is_active', 'must_change_password',
            'date_joined', 'last_login',
        ]
        read_only_fields = fields


class UserRoleAssignSerializer(serializers.Serializer):
    """جایگزینی کامل نقش‌های یک کاربر (idempotent) with admin-role policy (F2)."""
    role_ids = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    def validate_role_ids(self, roles):
        request = self.context['request']
        granting_admin = any(r.codename == SYSTEM_ADMIN_ROLE_CODENAME for r in roles)
        if granting_admin and not request.user.is_superuser:
            raise serializers.ValidationError(
                'فقط سوپریوزر می‌تواند نقش admin را اعطا کند.'
            )
        return roles

    def update(self, instance, validated_data):
        request = self.context['request']
        roles = validated_data['role_ids']
        new_has_admin = any(r.codename == SYSTEM_ADMIN_ROLE_CODENAME for r in roles)
        currently_has_admin = instance.has_role(SYSTEM_ADMIN_ROLE_CODENAME)

        # Only superuser may remove the admin role from a user.
        if currently_has_admin and not new_has_admin and not request.user.is_superuser:
            raise serializers.ValidationError(
                {'role_ids': 'فقط سوپریوزر می‌تواند نقش admin را حذف کند.'}
            )

        # Prevent removal of the last effective administrator.
        if currently_has_admin and not new_has_admin and not instance.is_superuser:
            other_role_admins = (
                User.objects.filter(
                    roles__codename=SYSTEM_ADMIN_ROLE_CODENAME,
                    roles__is_active=True,
                )
                .exclude(pk=instance.pk)
                .distinct()
            )
            other_superusers = User.objects.filter(is_superuser=True).exclude(pk=instance.pk)
            if not other_role_admins.exists() and not other_superusers.exists():
                raise serializers.ValidationError(
                    {'role_ids': 'نمی‌توان آخرین مدیر مؤثر سیستم را حذف کرد.'}
                )

        UserRole.objects.filter(user=instance).exclude(role__in=roles).delete()
        for role in roles:
            UserRole.objects.get_or_create(
                user=instance, role=role, defaults={'assigned_by': request.user}
            )
        return instance


class LoginSerializer(serializers.Serializer):
    """تنها راه ورود به سیستم. هیچ endpoint ثبت‌نامی وجود ندارد."""
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=_PASSWORD_MAX_LENGTH,
    )

    def validate(self, attrs):
        request = self.context['request']
        username = attrs.get('username', '').strip()
        password = attrs.get('password')

        try:
            user_obj = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # F6: run a password check against a dummy hash so timing is closer
            # to the existing-user path without creating a fake User row.
            check_password(password, _DUMMY_PASSWORD_HASH)
            raise serializers.ValidationError(_GENERIC_LOGIN_ERROR)

        # F5: locked and inactive use the same generic message as wrong password
        # to reduce account-existence enumeration.
        if user_obj.is_locked or not user_obj.is_active:
            check_password(password, user_obj.password)
            raise serializers.ValidationError(_GENERIC_LOGIN_ERROR)

        # Use the canonical username from the DB so case differences do not
        # cause a false authentication failure after an iexact lookup.
        user = authenticate(
            request=request,
            username=user_obj.username,
            password=password,
        )
        if user is None:
            user_obj.register_failed_attempt()
            raise serializers.ValidationError(_GENERIC_LOGIN_ERROR)

        user.reset_failed_attempts()
        attrs['user'] = user
        return attrs


class TokenResponseMixin:
    """تولید access/refresh token برای view هایی که بعد از موفقیت باید JWT بدهند"""

    @staticmethod
    def build_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class InviteLinkCreateSerializer(serializers.Serializer):
    """
    فقط ادمین این را پر می‌کند: username و password را خودش تعیین/تایید می‌کند.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=10,
        max_length=_PASSWORD_MAX_LENGTH,
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, required=False
    )
    expires_in_hours = serializers.IntegerField(default=48, min_value=1, max_value=24 * 14)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('این نام کاربری قبلاً استفاده شده است.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_role_ids(self, roles):
        # F2: ordinary admin cannot grant the admin role via invite either.
        request = self.context.get('request')
        if request is not None and not request.user.is_superuser:
            if any(r.codename == SYSTEM_ADMIN_ROLE_CODENAME for r in roles):
                raise serializers.ValidationError(
                    'فقط سوپریوزر می‌تواند نقش admin را اعطا کند.'
                )
        return roles


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserActivateSerializer(serializers.Serializer):
    """فقط برای مستندسازی Swagger بدنه‌ی PATCH فعال/غیرفعال‌سازی کاربر"""
    is_active = serializers.BooleanField()


class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class TokenPairResponseSerializer(serializers.Serializer):
    """شکل پاسخ لاگین موفق و مصرف موفق لینک دعوت، برای مستندسازی Swagger"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserMeSerializer()


class InviteLinkCreateResponseSerializer(serializers.Serializer):
    """شکل پاسخ ساخت لینک دعوت، برای مستندسازی Swagger"""
    user = UserSerializer()
    invite_url = serializers.CharField()
    token = serializers.CharField()
    expires_at = serializers.DateTimeField()
    warning = serializers.CharField()

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('نام کاربری الزامی است.')
        existing = User.objects.filter(username__iexact=value).first()
        if existing is None:
            return value
        # کاربر فعال: لینک دعوت جدید مجاز نیست
        if existing.is_active:
            raise serializers.ValidationError(
                'این نام کاربری مربوط به یک کاربر فعال است. برای دعوت مجدد ابتدا حساب را غیرفعال کنید.'
            )
        # کاربر غیرفعال: اجازه صدور/تمدید لینک با همان username
        self.context['existing_invite_user'] = existing
        return existing.username  # canonical case from DB
    
    

class RoleCodeNameSerializer(serializers.Serializer):
    """نقش خلاصه برای پاسخ ساخت کاربر: code داخلی + name فارسی."""
    code = serializers.CharField(source='codename')
    name = serializers.CharField()


class UserCreateResponseSerializer(serializers.ModelSerializer):
    """پاسخ امن ساخت کاربر — بدون password و فیلدهای حساس."""
    role = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'role', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_role(self, obj):
        role = obj.roles.filter(is_active=True).order_by('codename').first()
        if role is None:
            return None
        return RoleCodeNameSerializer(role).data


class UserCreateSerializer(serializers.Serializer):
    """ساخت کاربر جدید توسط مدیر دارای users.create."""
    username = serializers.CharField(max_length=150, help_text='نام کاربری (یکتا)')
    email = serializers.EmailField(
        required=False, allow_blank=True, allow_null=True, help_text='ایمیل کاربر',
    )
    first_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True, help_text='نام',
    )
    last_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True, help_text='نام خانوادگی',
    )
    password = serializers.CharField(
        write_only=True,
        min_length=10,
        max_length=_PASSWORD_MAX_LENGTH,
        help_text='رمز عبور',
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=10,
        max_length=_PASSWORD_MAX_LENGTH,
        help_text='تکرار رمز عبور',
        style={'input_type': 'password'},
    )
    role = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='کد نقش (admin / curator / viewer) — اختیاری',
    )
    is_active = serializers.BooleanField(
        required=False, default=True, help_text='فعال بودن کاربر',
    )

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('نام کاربری الزامی است.')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('این نام کاربری قبلاً ثبت شده است.')
        return value

    def validate_email(self, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            return None
        qs = User.objects.filter(email__iexact=value).exclude(email='').exclude(email__isnull=True)
        if qs.exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_role(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        value = value.strip().lower()
        try:
            role = Role.objects.get(codename=value, is_active=True)
        except Role.DoesNotExist:
            raise serializers.ValidationError('نقش انتخاب‌شده معتبر نیست.')
        return role

    def validate(self, attrs):
        password = attrs.get('password')
        confirm = attrs.get('password_confirm')
        if password != confirm:
            raise serializers.ValidationError({
                'password_confirm': ['تکرار رمز عبور با رمز عبور یکسان نیست.'],
            })
        role = attrs.get('role')
        request = self.context.get('request')
        if (
            role is not None
            and role.codename == SYSTEM_ADMIN_ROLE_CODENAME
            and request is not None
            and not request.user.is_superuser
        ):
            raise serializers.ValidationError({
                'role': ['فقط سوپریوزر می‌تواند نقش admin را اعطا کند.'],
            })
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        role = validated_data.pop('role', None)
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        is_active = validated_data.pop('is_active', True)
        email = validated_data.get('email') or None
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            email=email,
            first_name=validated_data.get('first_name') or '',
            last_name=validated_data.get('last_name') or '',
            is_active=is_active,
            created_by=request.user if request.user.is_authenticated else None,
        )
        if role is not None:
            UserRole.objects.create(user=user, role=role, assigned_by=request.user)
        return user
