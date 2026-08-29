"""
انگشتر archive models.
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


class Ring(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name='نام')
    category = models.ForeignKey(
        'categories.Category', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rings_items', verbose_name='دسته‌بندی',
    )

    # انگشتر
    metal = models.CharField(max_length=100, blank=True, default='', verbose_name='فلز (طلا، نقره، ...)')
    purity = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='عیار (%)')
    stone_type = models.CharField(max_length=100, blank=True, default='', verbose_name='نوع سنگ')
    stone_color = models.CharField(max_length=80, blank=True, default='', verbose_name='رنگ سنگ')
    stone_weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='وزن سنگ (قیراط/گرم)')
    ring_size = models.CharField(max_length=30, blank=True, default='', verbose_name='سایز انگشتر')
    weight = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='وزن کل (گرم)')
    style = models.CharField(max_length=100, blank=True, default='', verbose_name='سبک')
    engraving = models.TextField(blank=True, default='', verbose_name='حکاکی')
    maker_mark = models.CharField(max_length=100, blank=True, default='', verbose_name='نشان سازنده')
    is_set = models.BooleanField(default=False, verbose_name='دارای نگین')


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
        verbose_name = 'انگشتر'
        verbose_name_plural = 'انگشترها'
        indexes = [
            models.Index(fields=['country', 'year']),
            models.Index(fields=['catalog_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        year_part = f' ({self.year})' if self.year else ''
        return f'{self.name}{year_part}'


from .related_models import (  # noqa: E402
    RingImage,
    RingImageType,
    RingPurchaseRecord,
    RingValuationRecord,
)
