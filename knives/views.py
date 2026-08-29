from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import KnifeFilter
from .models import Knife, KnifeImage
from .serializers import KnifeImageSerializer, KnifeListSerializer, KnifeSerializer


@extend_schema_view(
    list=extend_schema(tags=['چاقو'], summary='لیست چاقوها', description='**دسترسی:** `knives.view`'),
    retrieve=extend_schema(tags=['چاقو'], summary='جزئیات چاقو', description='**دسترسی:** `knives.view`'),
    create=extend_schema(tags=['چاقو'], summary='ثبت چاقو', description='**دسترسی:** `knives.create`'),
    update=extend_schema(tags=['چاقو'], summary='ویرایش کامل', description='**دسترسی:** `knives.update`'),
    partial_update=extend_schema(tags=['چاقو'], summary='ویرایش جزئی', description='**دسترسی:** `knives.update`'),
    destroy=extend_schema(tags=['چاقو'], summary='حذف', description='**دسترسی:** `knives.delete`'),
)
class KnifeViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'knives.view',
        'retrieve': 'knives.view',
        'create': 'knives.create',
        'update': 'knives.update',
        'partial_update': 'knives.update',
        'destroy': 'knives.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = KnifeFilter
    search_fields = ['name', 'country', 'knife_type', 'blade_material', 'origin_region', 'maker', 'catalog_number', 'notes']
    ordering_fields = ['name', 'year', 'blade_length', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Knife.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return KnifeListSerializer
        return KnifeSerializer


class KnifeNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Knife, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر چاقو'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر چاقو'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر چاقو'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر چاقو'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر چاقو'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر چاقو'], summary='حذف تصویر'),
)
class KnifeImageViewSet(KnifeNestedMixin, viewsets.ModelViewSet):
    serializer_class = KnifeImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'knives.view', 'retrieve': 'knives.view',
        'create': 'knives.update', 'update': 'knives.update',
        'partial_update': 'knives.update', 'destroy': 'knives.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return KnifeImage.objects.none()
        return KnifeImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
