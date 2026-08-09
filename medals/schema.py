"""OpenAPI / Swagger documentation helpers for medals (Persian)."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

# ---------------------------------------------------------------------------
# Shared query parameters for medal list / search
# ---------------------------------------------------------------------------

MEDAL_LIST_PARAMETERS = [
    OpenApiParameter(
        name='search',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'جستجوی متنی در نام، کشور، مناسبت، دوره تاریخی، سازنده، '
            'ضرابخانه، شماره کاتالوگ، جنس و یادداشت.'
        ),
    ),
    OpenApiParameter(
        name='country',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر دقیق کشور (بدون حساسیت به حروف بزرگ/کوچک). مثال: Iran',
    ),
    OpenApiParameter(
        name='country_contains',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر کشور به‌صورت شامل (icontains).',
    ),
    OpenApiParameter(
        name='material',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر جنس (شامل). مثال: gold، silver',
    ),
    OpenApiParameter(
        name='quality',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'درجه کیفیت (دقیق). مقادیر مجاز: '
            'UNC (بدون گردش)، AU، XF (بسیار عالی)، VF (خیلی خوب)، F (خوب)، '
            'VG، G، AG، FAIR، POOR، OTHER'
        ),
    ),
    OpenApiParameter(
        name='authenticity',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'وضعیت اصالت. مقادیر: authentic، suspect، counterfeit، '
            'unverified، unknown'
        ),
    ),
    OpenApiParameter(
        name='category',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='شناسه دسته‌بندی (category_id).',
    ),
    OpenApiParameter(
        name='maker',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر سازنده (شامل).',
    ),
    OpenApiParameter(
        name='occasion',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر مناسبت (شامل).',
    ),
    OpenApiParameter(
        name='catalog_number',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر شماره کاتالوگ (شامل).',
    ),
    OpenApiParameter(
        name='historical_period',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر دوره تاریخی (شامل).',
    ),
    OpenApiParameter(
        name='year',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='فیلتر دقیق سال ساخت.',
    ),
    OpenApiParameter(
        name='year_min',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداقل سال ساخت (شامل).',
    ),
    OpenApiParameter(
        name='year_max',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداکثر سال ساخت (شامل).',
    ),
    OpenApiParameter(
        name='weight_min',
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداقل وزن به گرم.',
    ),
    OpenApiParameter(
        name='weight_max',
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداکثر وزن به گرم.',
    ),
    OpenApiParameter(
        name='diameter_min',
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداقل قطر به میلی‌متر.',
    ),
    OpenApiParameter(
        name='diameter_max',
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        required=False,
        description='حداکثر قطر به میلی‌متر.',
    ),
    OpenApiParameter(
        name='ordering',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'مرتب‌سازی. فیلدهای مجاز: name, year, created_at, updated_at, '
            'purchase_date, weight, diameter, current_value. '
            'برای نزولی پیشوند - بگذارید. مثال: -year'
        ),
    ),
    OpenApiParameter(
        name='page',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        required=False,
        description='شماره صفحه برای صفحه‌بندی (پیش‌فرض ۱). اندازه هر صفحه: ۲۰.',
    ),
]

MEDAL_CREATE_EXAMPLE = OpenApiExample(
    'نمونه ایجاد مدال',
    value={
        'name': 'مدال یادبود تاج‌گذاری',
        'country': 'Iran',
        'year': 1967,
        'occasion': 'تاج‌گذاری',
        'historical_period': 'پهلوی',
        'maker': 'ضرابخانه تهران',
        'material': 'نقره',
        'weight': '25.50',
        'diameter': '40.00',
        'quality': 'XF',
        'authenticity': 'authentic',
        'catalog_number': 'CAT-001',
        'purchase_price': '1500000',
        'purchase_currency': 'IRR',
        'notes': 'نمونه آرشیوی',
    },
    request_only=True,
)

IMAGE_TYPE_HELP = (
    'نوع تصویر. مقادیر مجاز: front (رو)، back (پشت)، edge (لبه)، '
    'packaging (بسته‌بندی)، certificate (گواهی)، invoice (فاکتور)، other (سایر)'
)

FILE_TYPE_HELP = (
    'نوع فایل. مقادیر مجاز: certificate (گواهی)، invoice (فاکتور)، '
    'document (سند)، other (سایر). فرمت‌های مجاز: pdf, txt, doc, docx, '
    'odt, rtf, csv, xls, xlsx. فایل‌های اجرایی مجاز نیستند.'
)
