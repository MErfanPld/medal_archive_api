from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions as drf_permissions, filters, mixins
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.permissions import HasAppPermission

from .filters import MedalFilter
from .models import Medal, MedalImage, MedalFile, MedalPurchaseRecord, MedalValuationRecord
from .serializers import (
    MedalSerializer, MedalImageSerializer, MedalFileSerializer,
    MedalPurchaseRecordSerializer, MedalValuationRecordSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Medals'], summary='List/search medals'),
    retrieve=extend_schema(tags=['Medals'], summary='Retrieve medal'),
    create=extend_schema(tags=['Medals'], summary='Create medal'),
    update=extend_schema(tags=['Medals'], summary='Update medal'),
    partial_update=extend_schema(tags=['Medals'], summary='Partial update medal'),
    destroy=extend_schema(tags=['Medals'], summary='Delete medal'),
)
class MedalViewSet(viewsets.ModelViewSet):
    serializer_class = MedalSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.create',
        'update': 'medals.update', 'partial_update': 'medals.update', 'destroy': 'medals.delete',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedalFilter
    search_fields = ['name', 'country', 'occasion', 'historical_period', 'maker', 'mint_or_manufacturer', 'catalog_number', 'notes', 'material']
    ordering_fields = ['name', 'year', 'created_at', 'updated_at', 'purchase_date', 'weight', 'diameter', 'current_value']
    ordering = ['-created_at']

    def get_queryset(self):
        return Medal.objects.select_related('category').prefetch_related('images').all()


class MedalNestedMixin:
    medal_url_kwarg = 'medal_pk'

    def get_medal(self):
        return get_object_or_404(Medal, pk=self.kwargs[self.medal_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['medal'] = self.get_medal()
        return ctx


class MedalImageViewSet(MedalNestedMixin, viewsets.ModelViewSet):
    serializer_class = MedalImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.update',
        'update': 'medals.update', 'partial_update': 'medals.update', 'destroy': 'medals.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return MedalImage.objects.filter(medal_id=self.kwargs['medal_pk']).select_related('uploaded_by')


class MedalFileViewSet(MedalNestedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = MedalFileSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.update', 'destroy': 'medals.update'}
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return MedalFile.objects.filter(medal_id=self.kwargs['medal_pk']).select_related('uploaded_by')


class MedalPurchaseRecordViewSet(MedalNestedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = MedalPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.update', 'destroy': 'medals.update'}

    def get_queryset(self):
        return MedalPurchaseRecord.objects.filter(medal_id=self.kwargs['medal_pk']).select_related('created_by')


class MedalValuationRecordViewSet(MedalNestedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = MedalValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.update', 'destroy': 'medals.update'}

    def get_queryset(self):
        return MedalValuationRecord.objects.filter(medal_id=self.kwargs['medal_pk']).select_related('created_by')
