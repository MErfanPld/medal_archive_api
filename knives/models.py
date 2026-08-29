"""
چاقو archive models.
"""
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class AuthenticityStatus(models.TextChoices):
    AUTHENTIC = 'authentic', 'اصلی'
    SUSPECT = 'suspect', 'مشکوک'
    COUNTERFEIT = 'counterfeit', 'جعلی'
    UNVERIFIED = 'unverified', 'تأییدنشده'
    UNKNOWN = 'unknown', 'نامشخص'


class PurchaseCurrency(models.TextChoices):
    IRR = 'IRR', 'ریال ایران'
    USD = 'USD', 'دلار آمریکا'
    EUR = 'EUR', 'یورو'
    GBP = 'GBP', 'پوند'
    TRY = 'TRY', 'لیر ترکیه'
    AED = 'AED', 'درهم امارات'
    OTHER = 'OTHER', 'سایر'


class ConditionGrade(models.TextChoices):
    EXCELLENT = 'excellent', 'عالی'
    GOOD = 'good', 'خوب'
    FAIR = 'fair', 'متوسط'
    POOR = 'poor', 'ضعیف'
    OTHER = 'other', 'سایر'


class Knife(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name='نام')
    category = models.ForeignKey(
        'categories.Category', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='knives_items', verbose_name='دسته‌بندی',
    )

    # چاقو
    knife_type = models.CharField(max_length=100, blank=True, default='', verbose_name='نوع (ضمیر، شکاری، تاشو، ...)')
    blade_material = models.CharField(max_length=100, blank=True, default='', verbose_name='جنس تیغه')
    blade_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='طول تیغه (سانتی‌متر)')
    total_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='طول کل (سانتی‌متر)')
    handle_material = models.CharField(max_length=100, blank=True, default='', verbose_name='جنس دسته')
    handle_decoration = models.CharField(max_length=200, blank=True, default='', verbose_name='تزیین دسته')
    sheath_material = models.CharField(max_length=100, blank=True, default='', verbose_name='جنس غلاف')
    origin_region = models.CharField(max_length=150, blank=True, default='', verbose_name='منطقه ساخت (زنجان، ...)')
    maker = models.CharField(max_length=150, blank=True, default='', verbose_name='سازنده')
    weight = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='وزن (گرم)')
    has_sheath = models.BooleanField(default=False, verbose_name='دارای غلاف')


    # مشترک آرشیو
    country = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name='کشور')
    year = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True, verbose_name='سال')
    historical_period = models.CharField(max_length=150, blank=True, default='', verbose_name='دوره تاریخی')
    catalog_number = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name='شماره کاتالوگ')
    condition = models.CharField(max_length=20, choices=ConditionGrade.choices, blank=True, default='', verbose_name='وضعیت')
    authenticity = models.CharField(max_length=20, choices=AuthenticityStatus.choices, default=AuthenticityStatus.UNKNOWN, db_index=True, verbose_name='اصالت')
    purchase_date = models.DateField(null=True, blank=True, verbose_name='تاریخ خرید')
    purchase_location = models.CharField(max_length=255, blank=True, default='', verbose_name='محل خرید')
    seller = models.CharField(max_length=150, blank=True, default='', verbose_name='فروشنده')
    purchase_price = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='قیمت خرید')
    purchase_currency = models.CharField(max_length=10, choices=PurchaseCurrency.choices, blank=True, default='', verbose_name='واحد پول خرید')
    current_value = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='ارزش فعلی')
    last_valuation_date = models.DateField(null=True, blank=True, verbose_name='تاریخ آخرین ارزیابی')
    cabinet_number = models.CharField(max_length=50, blank=True, default='', verbose_name='کمد')
    drawer_number = models.CharField(max_length=50, blank=True, default='', verbose_name='کشو')
    box_number = models.CharField(max_length=50, blank=True, default='', verbose_name='جعبه')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'چاقو'
        verbose_name_plural = 'چاقوها'
        indexes = [
            models.Index(fields=['country', 'year']),
            models.Index(fields=['catalog_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        year_part = f' ({self.year})' if self.year else ''
        return f'{self.name}{year_part}'


from .related_models import (  # noqa: E402
    KnifeImage,
    KnifeImageType,
    KnifePurchaseRecord,
    KnifeValuationRecord,
)
