from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions as drf_permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from users.permissions import HasAppPermission

from .filters import BanknoteFilter
from .models import Banknote, BanknoteImage
from .serializers import BanknoteImageSerializer, BanknoteListSerializer, BanknoteSerializer


@extend_schema_view(
    list=extend_schema(tags=['اسکناس'], summary='لیست اسکناس‌ها', description='**دسترسی:** `banknotes.view`'),
    retrieve=extend_schema(tags=['اسکناس'], summary='جزئیات اسکناس', description='**دسترسی:** `banknotes.view`'),
    create=extend_schema(tags=['اسکناس'], summary='ثبت اسکناس', description='**دسترسی:** `banknotes.create`'),
    update=extend_schema(tags=['اسکناس'], summary='ویرایش کامل', description='**دسترسی:** `banknotes.update`'),
    partial_update=extend_schema(tags=['اسکناس'], summary='ویرایش جزئی', description='**دسترسی:** `banknotes.update`'),
    destroy=extend_schema(tags=['اسکناس'], summary='حذف', description='**دسترسی:** `banknotes.delete`'),
)
class BanknoteViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'banknotes.view',
        'retrieve': 'banknotes.view',
        'create': 'banknotes.create',
        'update': 'banknotes.update',
        'partial_update': 'banknotes.update',
        'destroy': 'banknotes.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BanknoteFilter
    search_fields = ['name', 'country', 'serial_number', 'series', 'catalog_number', 'printer', 'notes']
    ordering_fields = ['name', 'year', 'face_value', 'current_value', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Banknote.objects.select_related('category').prefetch_related('images').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BanknoteListSerializer
        return BanknoteSerializer


class BanknoteNestedMixin:
    item_url_kwarg = 'item_pk'

    def get_item(self):
        return get_object_or_404(Banknote, pk=self.kwargs[self.item_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['item'] = self.get_item()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر اسکناس'], summary='لیست تصاویر'),
    retrieve=extend_schema(tags=['تصاویر اسکناس'], summary='جزئیات تصویر'),
    create=extend_schema(tags=['تصاویر اسکناس'], summary='افزودن تصویر'),
    update=extend_schema(tags=['تصاویر اسکناس'], summary='ویرایش تصویر'),
    partial_update=extend_schema(tags=['تصاویر اسکناس'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر اسکناس'], summary='حذف تصویر'),
)
class BanknoteImageViewSet(BanknoteNestedMixin, viewsets.ModelViewSet):
    serializer_class = BanknoteImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'banknotes.view', 'retrieve': 'banknotes.view',
        'create': 'banknotes.update', 'update': 'banknotes.update',
        'partial_update': 'banknotes.update', 'destroy': 'banknotes.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BanknoteImage.objects.none()
        return BanknoteImage.objects.filter(item_id=self.kwargs['item_pk']).select_related('uploaded_by')
