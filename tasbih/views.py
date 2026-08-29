from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import TasbihFilter
from .models import Tasbih, TasbihImage
from .serializers import TasbihImageSerializer, TasbihListSerializer, TasbihSerializer


@extend_schema_view(
    list=extend_schema(tags=['تسبیح'], summary='لیست تسبیح‌ها', description='**دسترسی:** `tasbih.view`'),
    retrieve=extend_schema(tags=['تسبیح'], summary='جزئیات تسبیح', description='**دسترسی:** `tasbih.view`'),
    create=extend_schema(tags=['تسبیح'], summary='ثبت تسبیح', description='**دسترسی:** `tasbih.create`'),
    update=extend_schema(tags=['تسبیح'], summary='ویرایش کامل', description='**دسترسی:** `tasbih.update`'),
    partial_update=extend_schema(tags=['تسبیح'], summary='ویرایش جزئی', description='**دسترسی:** `tasbih.update`'),
    destroy=extend_schema(tags=['تسبیح'], summary='حذف', description='**دسترسی:** `tasbih.delete`'),
)
class TasbihViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'tasbih.view',
        'retrieve': 'tasbih.view',
        'create': 'tasbih.create',
        'update': 'tasbih.update',
        'partial_update': 'tasbih.update',
        'destroy': 'tasbih.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TasbihFilter
    search_fields = ['name', 'country', 'bead_material', 'catalog_number', 'origin_mine', 'notes']
    ordering_fields = ['name', 'year', 'bead_count', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Tasbih.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TasbihListSerializer
        return TasbihSerializer


class TasbihNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Tasbih, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر تسبیح'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر تسبیح'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر تسبیح'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر تسبیح'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر تسبیح'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر تسبیح'], summary='حذف تصویر'),
)
class TasbihImageViewSet(TasbihNestedMixin, viewsets.ModelViewSet):
    serializer_class = TasbihImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'tasbih.view', 'retrieve': 'tasbih.view',
        'create': 'tasbih.update', 'update': 'tasbih.update',
        'partial_update': 'tasbih.update', 'destroy': 'tasbih.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TasbihImage.objects.none()
        return TasbihImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
