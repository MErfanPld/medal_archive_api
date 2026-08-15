from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import generics, status, permissions as drf_permissions, filters as drf_filters
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, Role, Permission, InviteLink, generate_raw_token, hash_token, UserRole
from .permissions import (
    HasAppPermission,
    SYSTEM_ADMIN_ROLE_CODENAME,
    SYSTEM_ROLE_CODENAMES,
)
from .throttles import LoginRateThrottle, InviteConsumeThrottle, InviteCreateThrottle
from .serializers import (
    LoginSerializer, UserSerializer, UserMeSerializer, RoleSerializer, PermissionSerializer,
    InviteLinkCreateSerializer, UserRoleAssignSerializer, TokenResponseMixin,
    LogoutSerializer, UserActivateSerializer, MessageResponseSerializer,
    TokenPairResponseSerializer, InviteLinkCreateResponseSerializer,
    UserCreateSerializer, UserCreateResponseSerializer,
)


def get_client_ip(request):
    if getattr(settings, 'USE_X_FORWARDED_FOR', False):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class LoginAPIView(TokenResponseMixin, APIView):
    permission_classes = [drf_permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(tags=['Auth'], summary='ورود کاربر', request=LoginSerializer, responses={200: TokenPairResponseSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login', 'last_login_ip'])
        tokens = self.build_tokens(user)
        return Response({**tokens, 'user': UserMeSerializer(user).data}, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='خروج کاربر', request=LogoutSerializer, responses={205: None, 400: MessageResponseSerializer})
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token الزامی است.'}, status=400)
        try:
            token = RefreshToken(refresh_token)
        except TokenError:
            return Response({'detail': 'توکن نامعتبر است.'}, status=400)
        token_user_id = token.get('user_id')
        if token_user_id is None or int(token_user_id) != int(request.user.id):
            return Response({'detail': 'این توکن متعلق به کاربر جاری نیست.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            token.blacklist()
        except TokenError:
            return Response({'detail': 'توکن نامعتبر است.'}, status=400)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeAPIView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated]

    @extend_schema(tags=['Auth'], summary='اطلاعات کاربر جاری', responses={200: UserMeSerializer})
    def get(self, request):
        return Response(UserMeSerializer(request.user).data)


class InviteLinkCreateAPIView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    required_permission = 'users.create'
    throttle_classes = [InviteCreateThrottle]

    @extend_schema(tags=['Invites'], summary='ساخت لینک دعوت یک‌بار مصرف', request=InviteLinkCreateSerializer, responses={201: InviteLinkCreateResponseSerializer})
    @transaction.atomic
    def post(self, request):
        serializer = InviteLinkCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = (data.get('email') or '').strip() or None
        user = User.objects.create_user(
            username=data['username'], password=data['password'], email=email,
            is_active=False, created_by=request.user,
        )
        for role in data.get('role_ids', []):
            UserRole.objects.create(user=user, role=role, assigned_by=request.user)
        raw_token = generate_raw_token()
        expires_at = timezone.now() + timezone.timedelta(hours=data['expires_in_hours'])
        invite = InviteLink.objects.create(
            user=user, token_hash=hash_token(raw_token), created_by=request.user,
            expires_at=expires_at, created_ip=get_client_ip(request),
        )
        frontend_base = getattr(settings, 'INVITE_LINK_FRONTEND_URL', '')
        invite_url = f'{frontend_base}?token={raw_token}' if frontend_base else raw_token
        return Response({
            'user': UserSerializer(user).data, 'invite_url': invite_url, 'token': raw_token,
            'expires_at': invite.expires_at,
            'warning': 'این توکن فقط همین یک‌بار نمایش داده می‌شود. جای دیگری ذخیره نشده است.',
        }, status=status.HTTP_201_CREATED)


class InviteLinkConsumeAPIView(TokenResponseMixin, APIView):
    permission_classes = [drf_permissions.AllowAny]
    throttle_classes = [InviteConsumeThrottle]

    @extend_schema(tags=['Invites'], summary='مصرف لینک دعوت', parameters=[OpenApiParameter(name='token', location=OpenApiParameter.PATH, type=OpenApiTypes.STR)], request=None, responses={200: TokenPairResponseSerializer, 404: MessageResponseSerializer, 410: MessageResponseSerializer})
    @transaction.atomic
    def post(self, request, token):
        token_hash = hash_token(token)
        try:
            invite = InviteLink.objects.select_for_update().select_related('user').get(token_hash=token_hash)
        except InviteLink.DoesNotExist:
            return Response({'detail': 'لینک نامعتبر است.'}, status=status.HTTP_404_NOT_FOUND)
        if invite.is_used:
            return Response({'detail': 'این لینک قبلاً استفاده شده است.'}, status=status.HTTP_410_GONE)
        if invite.is_expired:
            return Response({'detail': 'این لینک منقضی شده است.'}, status=status.HTTP_410_GONE)
        user = invite.user
        user.is_active = True
        user.save(update_fields=['is_active'])
        invite.is_used = True
        invite.used_at = timezone.now()
        invite.used_ip = get_client_ip(request)
        invite.save(update_fields=['is_used', 'used_at', 'used_ip'])
        tokens = self.build_tokens(user)
        return Response({**tokens, 'user': UserMeSerializer(user).data, 'detail': 'حساب کاربری با موفقیت فعال شد.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'])
class UserListAPIView(generics.ListCreateAPIView):
    """لیست کاربران (GET) و ساخت کاربر جدید (POST)."""
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'users.view',
        'create': 'users.create',
    }
    queryset = User.objects.all().prefetch_related('roles')
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['username', 'email']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(
        tags=['Users'],
        summary='لیست کاربران',
        description='لیست کاربران سیستم. نیاز به دسترسی users.view.',
        responses={200: UserSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Users'],
        summary='ساخت کاربر جدید',
        description=(
            'ایجاد کاربر توسط مدیر دارای دسترسی users.create. '
            'رمز عبور با الگوریتم هش پروژه ذخیره می‌شود و هرگز در پاسخ برنمی‌گردد. '
            'فیلد role اختیاری است و باید یکی از کدهای معتبر نقش باشد '
            '(admin, curator, viewer).'
        ),
        request=UserCreateSerializer,
        responses={
            201: UserCreateResponseSerializer,
            400: MessageResponseSerializer,
            401: MessageResponseSerializer,
            403: MessageResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserCreateResponseSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'retrieve': 'users.view', 'partial_update': 'users.update', 'update': 'users.update'}
    queryset = User.objects.all().prefetch_related('roles')

    @extend_schema(tags=['Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Users'], summary='فعال/غیرفعال کردن کاربر', request=UserActivateSerializer, responses={200: UserSerializer})
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if 'is_active' in request.data:
            user.is_active = bool(request.data['is_active'])
            user.save(update_fields=['is_active'])
        return Response(UserSerializer(user).data)


class UserRoleAssignAPIView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    required_permission = 'roles.assign'

    @extend_schema(tags=['Users'], operation_id='users_assign_roles', summary='جایگزینی کامل نقش‌های یک کاربر', request=UserRoleAssignSerializer, responses={200: UserSerializer})
    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserRoleAssignSerializer(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.clear_permission_cache()
        return Response(UserSerializer(user).data)


@extend_schema(tags=['ACL'])
class RoleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'list': 'roles.view', 'create': 'roles.create'}
    queryset = Role.objects.all().prefetch_related('permissions')


@extend_schema(tags=['ACL'])
class RoleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'retrieve': 'roles.view', 'update': 'roles.update', 'partial_update': 'roles.update', 'destroy': 'roles.delete'}
    queryset = Role.objects.all().prefetch_related('permissions')

    def perform_destroy(self, instance):
        if instance.codename in SYSTEM_ROLE_CODENAMES:
            raise PermissionDenied('نقش سیستمی admin قابل حذف نیست.')
        instance.delete()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.codename in SYSTEM_ROLE_CODENAMES:
            if 'is_active' in serializer.validated_data and not serializer.validated_data['is_active']:
                raise ValidationError({'is_active': 'نقش سیستمی admin را نمی‌توان غیرفعال کرد.'})
        serializer.save()


@extend_schema(tags=['ACL'])
class PermissionListAPIView(generics.ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    required_permission = 'permissions.view'
    queryset = Permission.objects.all()
