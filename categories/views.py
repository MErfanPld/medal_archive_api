from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions as drf_permissions, filters

from users.permissions import HasAppPermission

from .models import Category
from .serializers import CategorySerializer


@extend_schema_view(
    list=extend_schema(tags=['Categories'], summary='List categories'),
    retrieve=extend_schema(tags=['Categories'], summary='Retrieve category'),
    create=extend_schema(tags=['Categories'], summary='Create category'),
    update=extend_schema(tags=['Categories'], summary='Update category'),
    partial_update=extend_schema(tags=['Categories'], summary='Partial update category'),
    destroy=extend_schema(tags=['Categories'], summary='Delete category'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'categories.view',
        'retrieve': 'categories.view',
        'create': 'categories.create',
        'update': 'categories.update',
        'partial_update': 'categories.update',
        'destroy': 'categories.delete',
    }
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
