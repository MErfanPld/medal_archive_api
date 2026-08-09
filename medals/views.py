from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import viewsets, permissions as drf_permissions, filters, mixins
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
            '**زمان استفاده:** فرم افزودن مدال در پنل مدیریت.\n\n'
            '**دسترسی:** `medals.create` (معمولاً Admin / Curator / Superuser)\n\n'
            '**نکته:** فیلد `name` اجباری است. وزن، قطر، ضخامت و قیمت‌ها نمی‌توانند منفی باشند. '
            'تاریخ خرید و آخرین قیمت‌گذاری نمی‌تواند در آینده باشد.'
        ),
        examples=[MEDAL_CREATE_EXAMPLE],
    ),
    update=extend_schema(
        tags=['مدال‌ها'],
        summary='ویرایش کامل مدال (PUT)',
        description=(
            'تمام فیلدهای قابل ویرایش مدال را جایگزین می‌کند.\n\n'
            '**دسترسی:** `medals.update`'
        ),
    ),
    partial_update=extend_schema(
        tags=['مدال‌ها'],
        summary='ویرایش جزئی مدال (PATCH)',
        description=(
            'فقط فیلدهای ارسال‌شده را به‌روزرسانی می‌کند.\n\n'
            '**دسترسی:** `medals.update`'
        ),
    ),
    destroy=extend_schema(
        tags=['مدال‌ها'],
        summary='حذف مدال',
        description=(
            'مدال را حذف می‌کند. تصاویر، فایل‌ها و سوابق مرتبط نیز حذف می‌شوند '
            '(CASCADE).\n\n'
            '**دسترسی:** `medals.delete`'
        ),
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


class MedalNestedMixin:
    medal_url_kwarg = 'medal_pk'

    def get_medal(self):
        return get_object_or_404(Medal, pk=self.kwargs[self.medal_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['medal'] = self.get_medal()
        return ctx


@extend_schema_view(
    list=extend_schema(
        tags=['تصاویر مدال'],
        summary='دریافت تصاویر یک مدال',
        description=(
            'لیست تصاویر مرتبط با یک مدال را برمی‌گرداند.\n\n'
            '**دسترسی:** `medals.view`\n\n'
            f'**انواع تصویر:** {IMAGE_TYPE_HELP}'
        ),
    ),
    retrieve=extend_schema(
        tags=['تصاویر مدال'],
        summary='دریافت یک تصویر مدال',
        description='جزئیات یک تصویر شامل URL، نوع، ترتیب و وضعیت تصویر اصلی.\n\n**دسترسی:** `medals.view`',
    ),
    create=extend_schema(
        tags=['تصاویر مدال'],
        summary='افزودن تصویر به مدال',
        description=(
            'یک تصویر جدید برای مدال آپلود می‌کند (multipart/form-data).\n\n'
            '**دسترسی:** `medals.update`\n\n'
            '**محدودیت‌ها:**\n'
            '- حداکثر ۱۰ تصویر برای هر مدال\n'
            '- فرمت‌های مجاز: jpg, jpeg, png, webp, gif\n'
            '- حداکثر حجم: ۱۰ مگابایت (قابل تنظیم با MEDAL_IMAGE_MAX_BYTES)\n\n'
            '**فیلدها:**\n'
            '- `image` (اجباری): فایل تصویر\n'
            '- `image_type` (اختیاری): نوع تصویر\n'
            '- `caption` (اختیاری): عنوان\n'
            '- `ordering` (اختیاری): ترتیب نمایش\n'
            '- `is_primary` (اختیاری): اگر true باشد، سایر تصاویر primary نمی‌مانند\n\n'
            f'{IMAGE_TYPE_HELP}'
        ),
    ),
    update=extend_schema(
        tags=['تصاویر مدال'],
        summary='جایگزینی/ویرایش کامل تصویر',
        description='ویرایش کامل متادیتا یا جایگزینی فایل تصویر.\n\n**دسترسی:** `medals.update`',
    ),
    partial_update=extend_schema(
        tags=['تصاویر مدال'],
        summary='ویرایش جزئی تصویر',
        description='به‌روزرسانی جزئی فیلدهایی مانند caption، ordering، is_primary یا فایل.\n\n**دسترسی:** `medals.update`',
    ),
    destroy=extend_schema(
        tags=['تصاویر مدال'],
        summary='حذف تصویر مدال',
        description='تصویر را از مدال حذف می‌کند.\n\n**دسترسی:** `medals.update`',
    ),
)
class MedalImageViewSet(MedalNestedMixin, viewsets.ModelViewSet):
    serializer_class = MedalImageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view',
        'retrieve': 'medals.view',
        'create': 'medals.update',
        'update': 'medals.update',
        'partial_update': 'medals.update',
        'destroy': 'medals.update',
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalImage.objects.none()
        return MedalImage.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('uploaded_by')


@extend_schema_view(
    list=extend_schema(
        tags=['فایل‌های مدال'],
        summary='دریافت فایل‌های یک مدال',
        description=(
            'لیست فایل‌های مرتبط با مدال (گواهی، فاکتور، سند و …) را برمی‌گرداند.\n\n'
            f'**دسترسی:** `medals.view`\n\n{FILE_TYPE_HELP}'
        ),
    ),
    retrieve=extend_schema(
        tags=['فایل‌های مدال'],
        summary='دریافت یک فایل مدال',
        description='جزئیات یک فایل شامل URL، نوع و متادیتا.\n\n**دسترسی:** `medals.view`',
    ),
    create=extend_schema(
        tags=['فایل‌های مدال'],
        summary='افزودن فایل به مدال',
        description=(
            'فایل سند برای مدال آپلود می‌کند (multipart/form-data).\n\n'
            '**دسترسی:** `medals.update`\n\n'
            '**محدودیت‌ها:**\n'
            '- فرمت‌های مجاز: pdf, txt, doc, docx, odt, rtf, csv, xls, xlsx\n'
            '- فایل‌های اجرایی (exe و مشابه) رد می‌شوند\n'
            '- حداکثر حجم: ۲۰ مگابایت (MEDAL_FILE_MAX_BYTES)\n\n'
            '**فیلدها:**\n'
            '- `file` (اجباری)\n'
            '- `file_type` (اختیاری)\n'
            '- `notes` (اختیاری)\n\n'
            f'{FILE_TYPE_HELP}'
        ),
    ),
    destroy=extend_schema(
        tags=['فایل‌های مدال'],
        summary='حذف فایل مدال',
        description='فایل را حذف می‌کند.\n\n**دسترسی:** `medals.update`',
    ),
)
class MedalFileViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MedalFileSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view',
        'retrieve': 'medals.view',
        'create': 'medals.update',
        'destroy': 'medals.update',
    }
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalFile.objects.none()
        return MedalFile.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('uploaded_by')


@extend_schema_view(
    list=extend_schema(
        tags=['سوابق خرید'],
        summary='دریافت سوابق خرید مدال',
        description=(
            'لیست رکوردهای تاریخی خرید یک مدال را برمی‌گرداند.\n\n'
            'فیلدهای خرید روی خود مدال (purchase_date و …) snapshot فعلی هستند؛ '
            'این endpoint تاریخچه را نگه می‌دارد.\n\n'
            '**دسترسی:** `medals.view`'
        ),
    ),
    retrieve=extend_schema(
        tags=['سوابق خرید'],
        summary='دریافت یک سابقه خرید',
        description='جزئیات یک رکورد خرید.\n\n**دسترسی:** `medals.view`',
    ),
    create=extend_schema(
        tags=['سوابق خرید'],
        summary='ثبت سابقه خرید جدید',
        description=(
            'یک رکورد خرید تاریخی برای مدال ثبت می‌کند.\n\n'
            '**دسترسی:** `medals.update`\n\n'
            '**فیلدها:** purchase_date، location، seller، price، currency، notes\n'
            'قیمت نمی‌تواند منفی باشد.'
        ),
    ),
    destroy=extend_schema(
        tags=['سوابق خرید'],
        summary='حذف سابقه خرید',
        description='یک رکورد خرید را حذف می‌کند.\n\n**دسترسی:** `medals.update`',
    ),
)
class MedalPurchaseRecordViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MedalPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view',
        'retrieve': 'medals.view',
        'create': 'medals.update',
        'destroy': 'medals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalPurchaseRecord.objects.none()
        return MedalPurchaseRecord.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('created_by')


@extend_schema_view(
    list=extend_schema(
        tags=['سوابق ارزش‌گذاری'],
        summary='دریافت سوابق ارزش‌گذاری مدال',
        description=(
            'لیست ارزش‌گذاری‌های تاریخی مدال را برمی‌گرداند.\n\n'
            '**دسترسی:** `medals.view`'
        ),
    ),
    retrieve=extend_schema(
        tags=['سوابق ارزش‌گذاری'],
        summary='دریافت یک سابقه ارزش‌گذاری',
        description='جزئیات یک رکورد ارزش‌گذاری.\n\n**دسترسی:** `medals.view`',
    ),
    create=extend_schema(
        tags=['سوابق ارزش‌گذاری'],
        summary='ثبت ارزش‌گذاری جدید',
        description=(
            'یک رکورد ارزش‌گذاری جدید ثبت می‌کند و **snapshot** مدال را به‌روز می‌کند:\n'
            '- `Medal.current_value` ← مقدار جدید\n'
            '- `Medal.last_valuation_date` ← تاریخ ارزش‌گذاری\n\n'
            '**دسترسی:** `medals.update`\n\n'
            '**فیلدهای اجباری:** `value`, `valuation_date`\n'
            'تاریخ ارزش‌گذاری نمی‌تواند در آینده باشد. مقدار نمی‌تواند منفی باشد.'
        ),
    ),
    destroy=extend_schema(
        tags=['سوابق ارزش‌گذاری'],
        summary='حذف سابقه ارزش‌گذاری',
        description=(
            'رکورد ارزش‌گذاری را حذف می‌کند. توجه: snapshot روی مدال به‌صورت خودکار '
            'به عقب برنمی‌گردد.\n\n**دسترسی:** `medals.update`'
        ),
    ),
)
class MedalValuationRecordViewSet(
    MedalNestedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MedalValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'medals.view',
        'retrieve': 'medals.view',
        'create': 'medals.update',
        'destroy': 'medals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MedalValuationRecord.objects.none()
        return MedalValuationRecord.objects.filter(
            medal_id=self.kwargs['medal_pk']
        ).select_related('created_by')
