from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import viewsets, permissions as drf_permissions, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.permissions import HasAppPermission

from .filters import MedalFilter
from .models import (
    Medal,
    MedalImage,
    MedalFile,
    MedalPurchaseRecord,
    MedalValuationRecord,
)
from .schema import MEDAL_LIST_PARAMETERS, MEDAL_CREATE_EXAMPLE, IMAGE_TYPE_HELP, FILE_TYPE_HELP
from .serializers import (
    MedalSerializer,
    MedalImageSerializer,
    MedalFileSerializer,
    MedalPurchaseRecordSerializer,
    MedalValuationRecordSerializer,
    MuseumMedalSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['مدال‌ها'],
        summary='دریافت لیست مدال‌ها',
        description=(
            'فهرست مدال‌های ثبت‌شده در آرشیو را برمی‌گرداند.\n\n'
            '**زمان استفاده:** صفحه لیست مدال‌ها، جستجو و فیلتر پیشرفته.\n\n'
            '**احراز هویت:** Bearer Token الزامی است.\n'
            '**دسترسی:** `medals.view`\n\n'
            '**نقش‌ها:** Superuser، Admin، Curator، Viewer (در صورت داشتن مجوز).\n\n'
            '**صفحه‌بندی:** پاسخ شامل `count`, `next`, `previous`, `results` است '
            '(اندازه صفحه پیش‌فرض: ۲۰).\n\n'
            '**ترکیب فیلترها:** می‌توانید چند پارامتر را هم‌زمان بفرستید. مثال:\n'
            '`/api/medals/?country=Iran&year_min=1900&year_max=2000&material=gold&ordering=-year`'
        ),
        parameters=MEDAL_LIST_PARAMETERS,
    ),
    retrieve=extend_schema(
        tags=['مدال‌ها'],
        summary='دریافت جزئیات یک مدال',
        description=(
            'جزئیات کامل یک مدال شامل اطلاعات فیزیکی، خرید، ارزش، دسته‌بندی، '
            'تصویر اصلی و تعداد تصاویر را برمی‌گرداند.\n\n'
            '**دسترسی:** `medals.view`'
        ),
    ),
    create=extend_schema(
        tags=['مدال‌ها'],
        summary='ایجاد مدال جدید',
        description=(
            'یک مدال جدید در آرشیو ثبت می‌کند.\n\n'
            '**دسترسی:** `medals.create`'
        ),
        examples=[MEDAL_CREATE_EXAMPLE],
    ),
    update=extend_schema(
        tags=['مدال‌ها'],
        summary='ویرایش کامل مدال (PUT)',
        description='**دسترسی:** `medals.update`',
    ),
    partial_update=extend_schema(
        tags=['مدال‌ها'],
        summary='ویرایش جزئی مدال (PATCH)',
        description='**دسترسی:** `medals.update`',
    ),
    destroy=extend_schema(
        tags=['مدال‌ها'],
        summary='حذف مدال',
        description='**دسترسی:** `medals.delete`',
    ),
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
        'museum': 'medals.view',
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedalFilter
    search_fields = [
        'name', 'country', 'occasion', 'historical_period', 'maker',
        'mint_or_manufacturer', 'catalog_number', 'notes', 'material',
    ]
    ordering_fields = [
        'name', 'year', 'created_at', 'updated_at', 'purchase_date',
        'weight', 'diameter', 'current_value',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Medal.objects.select_related('category')
            .prefetch_related('images')
            .all()
        )

    @extend_schema(
        tags=['مدال‌ها'],
        summary='جزئیات موزه‌ای مدال',
        description=(
            'نمای غنی فقط‌خواندنی برای تجربه موزه/فرانت‌اند: هویت، مشخصات فیزیکی، '
            'اصالت، ارزش، تصاویر، اسناد، سوابق خرید و ارزش‌گذاری.\n\n'
            '**دسترسی:** `medals.view`\n'
            'با select_related / prefetch_related برای جلوگیری از N+1.'
        ),
        responses={200: MuseumMedalSerializer},
    )
    @action(detail=True, methods=['get'], url_path='museum')
    def museum(self, request, pk=None):
        medal = (
            Medal.objects.select_related('category')
            .prefetch_related(
                'images',
                'files',
                'purchase_records',
                'valuation_records',
            )
            .filter(pk=pk)
            .first()
        )
        if medal is None:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        return Response(MuseumMedalSerializer(medal, context={'request': request}).data)


class MedalNestedMixin:
    medal_url_kwarg = 'medal_pk'

    def get_medal(self):
        return get_object_or_404(Medal, pk=self.kwargs[self.medal_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['medal'] = self.get_medal()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['تصاویر مدال'], summary='دریافت تصاویر یک مدال'),
    retrieve=extend_schema(tags=['تصاویر مدال'], summary='دریافت یک تصویر مدال'),
    create=extend_schema(tags=['تصاویر مدال'], summary='افزودن تصویر به مدال'),
    update=extend_schema(tags=['تصاویر مدال'], summary='جایگزینی/ویرایش کامل تصویر'),
    partial_update=extend_schema(tags=['تصاویر مدال'], summary='ویرایش جزئی تصویر'),
    destroy=extend_schema(tags=['تصاویر مدال'], summary='حذف تصویر مدال'),
)
class MedalImageViewSet(MedalNestedMixin, viewsets.ModelViewSet):
    serializer_class = MedalImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view', 'create': 'medals.update',
        'update': 'medals.update', 'partial_update': 'medals.update', 'destroy': 'medals.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalImage.objects.none()
        return MedalImage.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('uploaded_by')


@extend_schema_view(
    list=extend_schema(tags=['فایل‌های مدال'], summary='دریافت فایل‌های یک مدال'),
    retrieve=extend_schema(tags=['فایل‌های مدال'], summary='دریافت یک فایل مدال'),
    create=extend_schema(tags=['فایل‌های مدال'], summary='افزودن فایل به مدال'),
    destroy=extend_schema(tags=['فایل‌های مدال'], summary='حذف فایل مدال'),
)
class MedalFileViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = MedalFileSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view',
        'create': 'medals.update', 'destroy': 'medals.update',
    }
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalFile.objects.none()
        return MedalFile.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('uploaded_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید'], summary='دریافت سوابق خرید مدال'),
    retrieve=extend_schema(tags=['سوابق خرید'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید'], summary='حذف سابقه خرید'),
)
class MedalPurchaseRecordViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = MedalPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view',
        'create': 'medals.update', 'destroy': 'medals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalPurchaseRecord.objects.none()
        return MedalPurchaseRecord.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری'], summary='دریافت سوابق ارزش‌گذاری مدال'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری'], summary='حذف سابقه ارزش‌گذاری'),
)
class MedalValuationRecordViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = MedalValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view', 'retrieve': 'medals.view',
        'create': 'medals.update', 'destroy': 'medals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalValuationRecord.objects.none()
        return MedalValuationRecord.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('created_by')
