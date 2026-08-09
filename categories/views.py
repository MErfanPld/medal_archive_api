from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import viewsets, permissions as drf_permissions, filters

from users.permissions import HasAppPermission

from .models import Category
from .serializers import CategorySerializer


CATEGORY_LIST_PARAMETERS = [
    OpenApiParameter(
        name='search',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='جستجو در نام، نامک (slug) و توضیحات دسته‌بندی.',
    ),
    OpenApiParameter(
        name='is_active',
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر وضعیت فعال/غیرفعال. true یا false',
    ),
    OpenApiParameter(
        name='ordering',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='مرتب‌سازی: name, created_at, updated_at (با - برای نزولی).',
    ),
    OpenApiParameter(
        name='page',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='شماره صفحه (اندازه صفحه: ۲۰).',
    ),
]


@extend_schema_view(
    list=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='دریافت لیست دسته‌بندی‌ها',
        description=(
            'فهرست دسته‌بندی‌های مدال را برمی‌گرداند.\n\n'
            '**زمان استفاده:** انتخاب دسته در فرم مدال، مدیریت دسته‌ها.\n\n'
            '**احراز هویت:** Bearer Token\n'
            '**دسترسی:** `categories.view`\n\n'
            'پاسخ صفحه‌بندی‌شده است (`count`, `next`, `previous`, `results`).'
        ),
        parameters=CATEGORY_LIST_PARAMETERS,
    ),
    retrieve=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='دریافت جزئیات دسته‌بندی',
        description='جزئیات یک دسته‌بندی شامل نام، نامک، توضیحات و وضعیت.\n\n**دسترسی:** `categories.view`',
    ),
    create=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='ایجاد دسته‌بندی جدید',
        description=(
            'یک دسته‌بندی جدید می‌سازد.\n\n'
            '**دسترسی:** `categories.create`\n\n'
            '**فیلدها:**\n'
            '- `name` (اجباری، یکتا): نام دسته‌بندی\n'
            '- `slug` (اختیاری، یکتا): اگر خالی باشد از نام ساخته می‌شود\n'
            '- `description` (اختیاری)\n'
            '- `is_active` (اختیاری، پیش‌فرض true)'
        ),
        examples=[
            OpenApiExample(
                'نمونه ایجاد دسته',
                value={'name': 'نظامی', 'description': 'مدال‌های نظامی', 'is_active': True},
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='ویرایش کامل دسته‌بندی (PUT)',
        description='جایگزینی کامل فیلدهای دسته‌بندی.\n\n**دسترسی:** `categories.update`',
    ),
    partial_update=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='ویرایش جزئی دسته‌بندی (PATCH)',
        description='به‌روزرسانی جزئی فیلدها.\n\n**دسترسی:** `categories.update`',
    ),
    destroy=extend_schema(
        tags=['دسته‌بندی‌ها'],
        summary='حذف دسته‌بندی',
        description=(
            'دسته‌بندی را حذف می‌کند. مدال‌های مرتبط معمولاً با SET_NULL از دسته جدا می‌شوند.\n\n'
            '**دسترسی:** `categories.delete`'
        ),
    ),
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
