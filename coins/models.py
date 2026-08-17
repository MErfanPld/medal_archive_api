"""
Coin & currency (سکه و پول) archive models.
Covers coins, banknotes, tokens and related monetary items.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class ItemType(models.TextChoices):
    COIN = 'coin', 'سکه'
    BANKNOTE = 'banknote', 'اسکناس'
    TOKEN = 'token', 'توکن / ژتون'
    BULLION = 'bullion', 'شمش / فلز گران‌بها'
    OTHER = 'other', 'سایر'


class QualityGrade(models.TextChoices):
    UNC = 'UNC', 'Uncirculated (UNC)'
    AU = 'AU', 'About Uncirculated (AU)'
    XF = 'XF', 'Extremely Fine (XF)'
    VF = 'VF', 'Very Fine (VF)'
    F = 'F', 'Fine (F)'
    VG = 'VG', 'Very Good (VG)'
    G = 'G', 'Good (G)'
    AG = 'AG', 'About Good (AG)'
    FAIR = 'FAIR', 'Fair'
    POOR = 'POOR', 'Poor'
    OTHER = 'OTHER', 'Other'


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


class Coin(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name='نام')
    item_type = models.CharField(
        max_length=20, choices=ItemType.choices, default=ItemType.COIN,
        db_index=True, verbose_name='نوع قلم',
    )
    category = models.ForeignKey(
        'categories.Category', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='coins', verbose_name='دسته‌بندی',
    )
    country = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name='کشور')
    year = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True, verbose_name='سال (میلادی)')
    year_hijri = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='سال (هجری / شمسی)')
    historical_period = models.CharField(max_length=150, blank=True, default='', db_index=True, verbose_name='دوره تاریخی')
    reign_or_ruler = models.CharField(max_length=150, blank=True, default='', verbose_name='حاکم / سلسله')
    face_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='ارزش اسمی')
    denomination = models.CharField(max_length=100, blank=True, default='', verbose_name='واحد اسمی (ریال، قران، ...)')
    currency_name = models.CharField(max_length=100, blank=True, default='', verbose_name='نام ارز / واحد پول')
    material = models.CharField(max_length=100, blank=True, default='', verbose_name='جنس / آلیاژ')
    purity = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='عیار به درصد', verbose_name='عیار (%)')
    weight = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, validators=[MinValueValidator(0)], help_text='گرم', verbose_name='وزن (گرم)')
    diameter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], help_text='میلی‌متر', verbose_name='قطر (میلی‌متر)')
    thickness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='ضخامت (میلی‌متر)')
    shape = models.CharField(max_length=80, blank=True, default='', verbose_name='شکل')
    edge = models.CharField(max_length=120, blank=True, default='', verbose_name='لبه')
    color = models.CharField(max_length=80, blank=True, default='', verbose_name='رنگ')
    serial_number = models.CharField(max_length=64, blank=True, default='', db_index=True, verbose_name='شماره سریال')
    series = models.CharField(max_length=120, blank=True, default='', verbose_name='سری / انتشار')
    signature = models.CharField(max_length=200, blank=True, default='', verbose_name='امضا / مقام مسئول')
    printer = models.CharField(max_length=150, blank=True, default='', verbose_name='چاپخانه')
    mint = models.CharField(max_length=150, blank=True, default='', verbose_name='ضرابخانه')
    maker = models.CharField(max_length=150, blank=True, default='', verbose_name='سازنده')
    mintage = models.PositiveIntegerField(null=True, blank=True, verbose_name='تیراژ')
    catalog_number = models.CharField(max_length=100, blank=True, default='', db_index=True, verbose_name='شماره کاتالوگ')
    quality = models.CharField(max_length=10, choices=QualityGrade.choices, blank=True, default='', db_index=True, verbose_name='کیفیت')
    preservation_condition = models.CharField(max_length=255, blank=True, default='', verbose_name='وضعیت نگهداری')
    authenticity = models.CharField(max_length=20, choices=AuthenticityStatus.choices, default=AuthenticityStatus.UNKNOWN, db_index=True, verbose_name='اصالت')
    is_proof = models.BooleanField(default=False, verbose_name='نسخه پروف (Proof)')
    is_commemorative = models.BooleanField(default=False, verbose_name='یادبودی')
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
        verbose_name = 'سکه / پول'
        verbose_name_plural = 'سکه‌ها و پول‌ها'
        indexes = [
            models.Index(fields=['country', 'year']),
            models.Index(fields=['item_type', 'country']),
            models.Index(fields=['catalog_number']),
            models.Index(fields=['quality']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        year_part = f' ({self.year})' if self.year else ''
        return f'{self.name}{year_part}'


from .related_models import (  # noqa: E402
    coin_image_upload_to,
    CoinImageType,
    CoinImage,
    CoinPurchaseRecord,
    CoinValuationRecord,
)
