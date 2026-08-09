from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import permissions as drf_permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import HasAppPermission

from . import services
from .pdf import ALLOWED_PDF_TYPES, build_pdf
from .serializers import (
    DashboardSummarySerializer,
    CountryReportSerializer,
    ValueReportSerializer,
    PurchaseReportSerializer,
)


class ReportsPermissionMixin:
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    required_permission = 'reports.view'


@extend_schema(
    tags=['گزارش‌ها'],
    summary='داشبورد و خلاصه آرشیو',
    description=(
        'آمار کلی مجموعه: تعداد مدال، کشورها، بازه سال، ارزش به‌تفکیک ارز، '
        'توزیع دسته‌بندی و کشور.\n\n'
        '**دسترسی:** `reports.view`\n'
        'ارزش‌ها هرگز بین ارزهای مختلف جمع نمی‌شوند.'
    ),
    responses={200: DashboardSummarySerializer},
)
class DashboardSummaryView(ReportsPermissionMixin, APIView):
    def get(self, request):
        data = services.dashboard_summary()
        return Response(DashboardSummarySerializer(data).data)


@extend_schema(
    tags=['گزارش‌ها'],
    summary='تحلیل کشورها (نمودار)',
    description=(
        'تعداد و درصد مدال‌ها به تفکیک کشور برای نمودارها.\n\n'
        '**Query:** `limit` (اختیاری) — حداکثر تعداد ردیف\n'
        '**دسترسی:** `reports.view`'
    ),
    parameters=[
        OpenApiParameter(
            name='limit', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
            required=False, description='حداکثر تعداد کشورها (مثلاً ۱۰ برای نمودار دایره‌ای)',
        ),
    ],
    responses={200: CountryReportSerializer},
)
class CountryReportView(ReportsPermissionMixin, APIView):
    def get(self, request):
        limit = request.query_params.get('limit')
        limit_int = int(limit) if limit and str(limit).isdigit() else None
        data = services.country_report(limit=limit_int)
        if data['total_medals'] == 0:
            data['items'] = []
        return Response(CountryReportSerializer(data).data)


@extend_schema(
    tags=['گزارش‌ها'],
    summary='تحلیل ارزش مجموعه',
    description=(
        'ارزش کل و توزیع ارزش بر اساس ارز، کشور، دسته و روند زمانی '
        '(از سوابق ارزش‌گذاری).\n\n'
        '**دسترسی:** `reports.view`\n'
        'بدون تبدیل نرخ ارز — فقط گروه‌بندی.'
    ),
    responses={200: ValueReportSerializer},
)
class ValueReportView(ReportsPermissionMixin, APIView):
    def get(self, request):
        return Response(ValueReportSerializer(services.value_report()).data)


@extend_schema(
    tags=['گزارش‌ها'],
    summary='گزارش خریدها',
    description=(
        'آمار خرید از سوابق خرید: سال، ارز، فروشنده، کشور.\n\n'
        '**دسترسی:** `reports.view`'
    ),
    responses={200: PurchaseReportSerializer},
)
class PurchaseReportView(ReportsPermissionMixin, APIView):
    def get(self, request):
        return Response(PurchaseReportSerializer(services.purchase_report()).data)


@extend_schema(
    tags=['گزارش‌ها'],
    summary='دانلود گزارش PDF',
    description=(
        'تولید PDF سمت سرور.\n\n'
        '**Query اجباری:** `type` یکی از: '
        '`summary`, `countries`, `valuation`, `purchases`, `inventory`\n\n'
        '**دسترسی:** `reports.view`\n'
        'مسیر فایل سیستم برگردانده نمی‌شود؛ پاسخ مستقیم application/pdf است.\n'
        'inventory حداکثر ۲۰۰ ردیف برای کنترل حجم.'
    ),
    parameters=[
        OpenApiParameter(
            name='type', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
            required=True,
            description='summary | countries | valuation | purchases | inventory',
            enum=list(sorted(ALLOWED_PDF_TYPES)),
        ),
    ],
    responses={
        200: OpenApiResponse(description='فایل PDF'),
        400: OpenApiResponse(description='نوع گزارش نامعتبر'),
    },
)
class PdfReportView(ReportsPermissionMixin, APIView):
    def get(self, request):
        report_type = (request.query_params.get('type') or '').strip().lower()
        if report_type not in ALLOWED_PDF_TYPES:
            return Response(
                {
                    'detail': 'Invalid report type.',
                    'allowed': sorted(ALLOWED_PDF_TYPES),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        pdf_bytes = build_pdf(report_type)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="medal_report_{report_type}.pdf"'
        )
        response['Content-Length'] = str(len(pdf_bytes))
        return response
