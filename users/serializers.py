from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role, Permission, UserRole


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

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        if permissions:
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
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


class UserRoleAssignSerializer(serializers.Serializer):
    """جایگزینی کامل نقش‌های یک کاربر (idempotent)"""
    role_ids = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    def update(self, instance, validated_data):
        request = self.context['request']
        roles = validated_data['role_ids']
        UserRole.objects.filter(user=instance).exclude(role__in=roles).delete()
        for role in roles:
            UserRole.objects.get_or_create(
                user=instance, role=role, defaults={'assigned_by': request.user}
            )
        return instance


class LoginSerializer(serializers.Serializer):
    """تنها راه ورود به سیستم. هیچ endpoint ثبت‌نامی وجود ندارد."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context['request']
        username = attrs.get('username', '').strip()
        password = attrs.get('password')

        try:
            user_obj = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # پیام یکسان برای جلوگیری از user enumeration
            raise serializers.ValidationError('نام کاربری یا رمز عبور اشتباه است.')

        if user_obj.is_locked:
            raise serializers.ValidationError(
                'حساب کاربری به دلیل تلاش‌های ناموفق مکرر موقتاً قفل شده است.'
            )

        if not user_obj.is_active:
            raise serializers.ValidationError('حساب کاربری فعال نیست.')

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            user_obj.register_failed_attempt()
            raise serializers.ValidationError('نام کاربری یا رمز عبور اشتباه است.')

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
    password = serializers.CharField(write_only=True, min_length=8)
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
    user = UserSerializer()


class InviteLinkCreateResponseSerializer(serializers.Serializer):
    """شکل پاسخ ساخت لینک دعوت، برای مستندسازی Swagger"""
    user = UserSerializer()
    invite_url = serializers.CharField()
    token = serializers.CharField()
    expires_at = serializers.DateTimeField()
    warning = serializers.CharField()