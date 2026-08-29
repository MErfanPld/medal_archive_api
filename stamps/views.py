from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import StampFilter
from .models import Stamp, StampImage
from .serializers import StampImageSerializer, StampListSerializer, StampSerializer


@extend_schema_view(
    list=extend_schema(tags=['تمبر'], summary='لیست تمبرها', description='**دسترسی:** `stamps.view`'),
    retrieve=extend_schema(tags=['تمبر'], summary='جزئیات تمبر', description='**دسترسی:** `stamps.view`'),
    create=extend_schema(tags=['تمبر'], summary='ثبت تمبر', description='**دسترسی:** `stamps.create`'),
    update=extend_schema(tags=['تمبر'], summary='ویرایش کامل', description='**دسترسی:** `stamps.update`'),
    partial_update=extend_schema(tags=['تمبر'], summary='ویرایش جزئی', description='**دسترسی:** `stamps.update`'),
    destroy=extend_schema(tags=['تمبر'], summary='حذف', description='**دسترسی:** `stamps.delete`'),
)
class StampViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'stamps.view',
        'retrieve': 'stamps.view',
        'create': 'stamps.create',
        'update': 'stamps.update',
        'partial_update': 'stamps.update',
        'destroy': 'stamps.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StampFilter
    search_fields = ['name', 'country', 'issue_name', 'catalog_number', 'catalog_scott', 'catalog_michel', 'theme', 'notes']
    ordering_fields = ['name', 'year', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Stamp.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return StampListSerializer
        return StampSerializer


class StampNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Stamp, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر تمبر'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر تمبر'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر تمبر'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر تمبر'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر تمبر'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر تمبر'], summary='حذف تصویر'),
)
class StampImageViewSet(StampNestedMixin, viewsets.ModelViewSet):
    serializer_class = StampImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'stamps.view', 'retrieve': 'stamps.view',
        'create': 'stamps.update', 'update': 'stamps.update',
        'partial_update': 'stamps.update', 'destroy': 'stamps.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StampImage.objects.none()
        return StampImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
