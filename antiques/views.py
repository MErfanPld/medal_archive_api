from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import AntiqueFilter
from .models import Antique, AntiqueImage
from .serializers import AntiqueImageSerializer, AntiqueListSerializer, AntiqueSerializer


@extend_schema_view(
    list=extend_schema(tags=['آنتیک'], summary='لیست آنتیک‌ها', description='**دسترسی:** `antiques.view`'),
    retrieve=extend_schema(tags=['آنتیک'], summary='جزئیات آنتیک', description='**دسترسی:** `antiques.view`'),
    create=extend_schema(tags=['آنتیک'], summary='ثبت آنتیک', description='**دسترسی:** `antiques.create`'),
    update=extend_schema(tags=['آنتیک'], summary='ویرایش کامل', description='**دسترسی:** `antiques.update`'),
    partial_update=extend_schema(tags=['آنتیک'], summary='ویرایش جزئی', description='**دسترسی:** `antiques.update`'),
    destroy=extend_schema(tags=['آنتیک'], summary='حذف', description='**دسترسی:** `antiques.delete`'),
)
class AntiqueViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'antiques.view',
        'retrieve': 'antiques.view',
        'create': 'antiques.create',
        'update': 'antiques.update',
        'partial_update': 'antiques.update',
        'destroy': 'antiques.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AntiqueFilter
    search_fields = ['name', 'country', 'object_type', 'material', 'style_period', 'maker', 'catalog_number', 'notes']
    ordering_fields = ['name', 'year', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Antique.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AntiqueListSerializer
        return AntiqueSerializer


class AntiqueNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Antique, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر آنتیک'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر آنتیک'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر آنتیک'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر آنتیک'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر آنتیک'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر آنتیک'], summary='حذف تصویر'),
)
class AntiqueImageViewSet(AntiqueNestedMixin, viewsets.ModelViewSet):
    serializer_class = AntiqueImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'antiques.view', 'retrieve': 'antiques.view',
        'create': 'antiques.update', 'update': 'antiques.update',
        'partial_update': 'antiques.update', 'destroy': 'antiques.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AntiqueImage.objects.none()
        return AntiqueImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
