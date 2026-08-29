from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import RingFilter
from .models import Ring, RingImage
from .serializers import RingImageSerializer, RingListSerializer, RingSerializer


@extend_schema_view(
    list=extend_schema(tags=['انگشتر'], summary='لیست انگشترها', description='**دسترسی:** `rings.view`'),
    retrieve=extend_schema(tags=['انگشتر'], summary='جزئیات انگشتر', description='**دسترسی:** `rings.view`'),
    create=extend_schema(tags=['انگشتر'], summary='ثبت انگشتر', description='**دسترسی:** `rings.create`'),
    update=extend_schema(tags=['انگشتر'], summary='ویرایش کامل', description='**دسترسی:** `rings.update`'),
    partial_update=extend_schema(tags=['انگشتر'], summary='ویرایش جزئی', description='**دسترسی:** `rings.update`'),
    destroy=extend_schema(tags=['انگشتر'], summary='حذف', description='**دسترسی:** `rings.delete`'),
)
class RingViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'rings.view',
        'retrieve': 'rings.view',
        'create': 'rings.create',
        'update': 'rings.update',
        'partial_update': 'rings.update',
        'destroy': 'rings.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RingFilter
    search_fields = ['name', 'country', 'metal', 'stone_type', 'catalog_number', 'maker_mark', 'notes']
    ordering_fields = ['name', 'year', 'weight', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Ring.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RingListSerializer
        return RingSerializer


class RingNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Ring, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر انگشتر'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر انگشتر'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر انگشتر'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر انگشتر'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر انگشتر'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر انگشتر'], summary='حذف تصویر'),
)
class RingImageViewSet(RingNestedMixin, viewsets.ModelViewSet):
    serializer_class = RingImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'rings.view', 'retrieve': 'rings.view',
        'create': 'rings.update', 'update': 'rings.update',
        'partial_update': 'rings.update', 'destroy': 'rings.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RingImage.objects.none()
        return RingImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
