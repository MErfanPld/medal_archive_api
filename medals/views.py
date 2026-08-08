from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions as drf_permissions, filters

from users.permissions import HasAppPermission

from .models import Medal
from .serializers import MedalSerializer


@extend_schema_view(
    list=extend_schema(tags=['Medals'], summary='List medals'),
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
        'list': 'medals.view',
        'retrieve': 'medals.view',
        'create': 'medals.create',
        'update': 'medals.update',
        'partial_update': 'medals.update',
        'destroy': 'medals.delete',
    }
    queryset = Medal.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category', 'country', 'year', 'quality', 'authenticity',
    ]
    search_fields = [
        'name', 'country', 'occasion', 'historical_period', 'maker',
        'mint_or_manufacturer', 'catalog_number', 'notes',
    ]
    ordering_fields = ['name', 'year', 'created_at', 'updated_at', 'purchase_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return Medal.objects.select_related('category').all()
