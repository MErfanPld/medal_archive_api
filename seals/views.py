from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import SealFilter
from .models import Seal, SealImage
from .serializers import SealImageSerializer, SealListSerializer, SealSerializer


@extend_schema_view(
    list=extend_schema(tags=['مهر'], summary='لیست مهرها', description='**دسترسی:** `seals.view`'),
    retrieve=extend_schema(tags=['مهر'], summary='جزئیات مهر', description='**دسترسی:** `seals.view`'),
    create=extend_schema(tags=['مهر'], summary='ثبت مهر', description='**دسترسی:** `seals.create`'),
    update=extend_schema(tags=['مهر'], summary='ویرایش کامل', description='**دسترسی:** `seals.update`'),
    partial_update=extend_schema(tags=['مهر'], summary='ویرایش جزئی', description='**دسترسی:** `seals.update`'),
    destroy=extend_schema(tags=['مهر'], summary='حذف', description='**دسترسی:** `seals.delete`'),
)
class SealViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'seals.view',
        'retrieve': 'seals.view',
        'create': 'seals.create',
        'update': 'seals.update',
        'partial_update': 'seals.update',
        'destroy': 'seals.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SealFilter
    search_fields = ['name', 'country', 'owner_name', 'inscription', 'catalog_number', 'material', 'notes']
    ordering_fields = ['name', 'year', 'weight', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Seal.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SealListSerializer
        return SealSerializer


class SealNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Seal, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر مهر'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر مهر'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر مهر'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر مهر'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر مهر'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر مهر'], summary='حذف تصویر'),
)
class SealImageViewSet(SealNestedMixin, viewsets.ModelViewSet):
    serializer_class = SealImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'seals.view', 'retrieve': 'seals.view',
        'create': 'seals.update', 'update': 'seals.update',
        'partial_update': 'seals.update', 'destroy': 'seals.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SealImage.objects.none()
        return SealImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
