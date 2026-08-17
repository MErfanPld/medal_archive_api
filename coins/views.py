from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import CoinFilter
from .models import Coin, CoinImage
from .serializers import CoinImageSerializer, CoinListSerializer, CoinSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['سکه و پول'],
        summary='لیست سکه‌ها و پول‌ها',
        description='**دسترسی:** `coins.view`',
    ),
    retrieve=extend_schema(
        tags=['سکه و پول'],
        summary='جزئیات یک قلم',
        description='**دسترسی:** `coins.view`',
    ),
    create=extend_schema(
        tags=['سکه و پول'],
        summary='ثبت سکه / اسکناس جدید',
        description='**دسترسی:** `coins.create`',
    ),
    update=extend_schema(
        tags=['سکه و پول'],
        summary='ویرایش کامل (PUT)',
        description='**دسترسی:** `coins.update`',
    ),
    partial_update=extend_schema(
        tags=['سکه و پول'],
        summary='ویرایش جزئی (PATCH)',
        description='**دسترسی:** `coins.update`',
    ),
    destroy=extend_schema(
        tags=['سکه و پول'],
        summary='حذف',
        description='**دسترسی:** `coins.delete`',
    ),
)
class CoinViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'coins.view',
        'retrieve': 'coins.view',
        'create': 'coins.create',
        'update': 'coins.update',
        'partial_update': 'coins.update',
        'destroy': 'coins.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CoinFilter
    search_fields = [
        'name', 'country', 'historical_period', 'reign_or_ruler',
        'denomination', 'currency_name', 'material', 'catalog_number',
        'serial_number', 'series', 'mint', 'maker', 'notes',
    ]
    ordering_fields = [
        'name', 'year', 'face_value', 'weight', 'current_value',
        'purchase_date', 'created_at', 'updated_at',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        return Coin.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CoinListSerializer
        return CoinSerializer


class CoinNestedMixin:
    coin_url_kwarg = 'coin_pk'

    def get_coin(self):
        return get_object_or_404(Coin, pk=self.kwargs[self.coin_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['coin'] = self.get_coin()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر سکه و پول'], summary='لیست تصاویر یک قلم'),
    retrieve=extend_schema(tags=['تصاویر سکه و پول'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر سکه و پول'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر سکه و پول'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر سکه و پول'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر سکه و پول'], summary='حذف تصویر'),
)
class CoinImageViewSet(CoinNestedMixin, viewsets.ModelViewSet):
    serializer_class = CoinImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'coins.view',
        'retrieve': 'coins.view',
        'create': 'coins.update',
        'update': 'coins.update',
        'partial_update': 'coins.update',
        'destroy': 'coins.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CoinImage.objects.none()
        return CoinImage.objects.filter(
            coin_id=self.kwargs['coin_pk']
        ).select_related('uploaded_by')
