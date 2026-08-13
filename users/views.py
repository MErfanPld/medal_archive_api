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
