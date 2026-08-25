"""
اسکناس archive models.
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


class Banknote(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name='نام')
    category = models.ForeignKey(
        'categories.Category', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='banknotes_items', verbose_name='دسته‌بندی',
    )

    # اسکناس
    face_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='ارزش اسمی')
    denomination = models.CharField(max_length=100, blank=True, default='', verbose_name='واحد (ریال، تومان، ...)')
    currency_name = models.CharField(max_length=100, blank=True, default='', verbose_name='نام ارز')
    serial_number = models.CharField(max_length=64, blank=True, default='', db_index=True, verbose_name='شماره سریال')
    series = models.CharField(max_length=120, blank=True, default='', verbose_name='سری / انتشار')
    signature = models.CharField(max_length=200, blank=True, default='', verbose_name='امضا')
    printer = models.CharField(max_length=150, blank=True, default='', verbose_name='چاپخانه')
    color = models.CharField(max_length=80, blank=True, default='', verbose_name='رنگ غالب')
    size_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='طول (میلی‌متر)')
    size_width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='عرض (میلی‌متر)')
    security_features = models.TextField(blank=True, default='', verbose_name='ویژگی‌های امنیتی')
    is_replacement = models.BooleanField(default=False, verbose_name='جایگزین (Replacement)')


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
        verbose_name = 'اسکناس'
        verbose_name_plural = 'اسکناس‌ها'
        indexes = [
            models.Index(fields=['country', 'year']),
            models.Index(fields=['catalog_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        year_part = f' ({self.year})' if self.year else ''
        return f'{self.name}{year_part}'


from .related_models import (  # noqa: E402
    BanknoteImage,
    BanknoteImageType,
    BanknotePurchaseRecord,
    BanknoteValuationRecord,
)
