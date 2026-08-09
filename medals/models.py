from django.core.validators import MinValueValidator
from django.db import models


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
    AUTHENTIC = 'authentic', 'Authentic'
    SUSPECT = 'suspect', 'Suspect'
    COUNTERFEIT = 'counterfeit', 'Counterfeit'
    UNVERIFIED = 'unverified', 'Unverified'
    UNKNOWN = 'unknown', 'Unknown'


class CurrencyCode(models.TextChoices):
    IRR = 'IRR', 'Iranian Rial'
    USD = 'USD', 'US Dollar'
    EUR = 'EUR', 'Euro'
    GBP = 'GBP', 'British Pound'
    TRY = 'TRY', 'Turkish Lira'
    AED = 'AED', 'UAE Dirham'
    OTHER = 'OTHER', 'Other'


class Medal(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name='نام مدال')
    country = models.CharField(
        max_length=100, blank=True, default='', db_index=True, verbose_name='کشور'
    )
    year = models.PositiveSmallIntegerField(
        null=True, blank=True, db_index=True, verbose_name='سال ساخت'
    )
    occasion = models.CharField(
        max_length=255, blank=True, default='', verbose_name='مناسبت'
    )
    historical_period = models.CharField(
        max_length=150, blank=True, default='', db_index=True, verbose_name='دوره تاریخی'
    )
    maker = models.CharField(
        max_length=150, blank=True, default='', verbose_name='سازنده'
    )
    mint_or_manufacturer = models.CharField(
        max_length=150, blank=True, default='', verbose_name='ضرابخانه یا کارخانه سازنده'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medals',
        verbose_name='دسته‌بندی',
    )

    material = models.CharField(
        max_length=100, blank=True, default='', verbose_name='جنس'
    )
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Weight in grams',
        verbose_name='وزن',
    )
    diameter = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Diameter in millimeters',
        verbose_name='قطر',
    )
    thickness = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Thickness in millimeters',
        verbose_name='ضخامت',
    )
    shape = models.CharField(
        max_length=80, blank=True, default='', verbose_name='شکل'
    )
    color = models.CharField(
        max_length=80, blank=True, default='', verbose_name='رنگ'
    )
    edge = models.CharField(
        max_length=80, blank=True, default='', verbose_name='لبه مدال'
    )

    quality = models.CharField(
        max_length=10, choices=QualityGrade.choices, blank=True, default='',
        db_index=True, verbose_name='کیفیت',
    )
    preservation_condition = models.CharField(
        max_length=255, blank=True, default='', verbose_name='وضعیت نگهداری'
    )
    authenticity = models.CharField(
        max_length=20,
        choices=AuthenticityStatus.choices,
        default=AuthenticityStatus.UNKNOWN,
        db_index=True,
        verbose_name='اصالت',
    )
    catalog_number = models.CharField(
        max_length=100, blank=True, default='', db_index=True, verbose_name='شماره کاتالوگ'
    )

    purchase_date = models.DateField(null=True, blank=True, verbose_name='تاریخ خرید')
    purchase_location = models.CharField(
        max_length=255, blank=True, default='', verbose_name='محل خرید'
    )
    seller = models.CharField(
        max_length=150, blank=True, default='', verbose_name='فروشنده'
    )
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت خرید',
    )
    purchase_currency = models.CharField(
        max_length=10, choices=CurrencyCode.choices, blank=True, default='',
        verbose_name='واحد پول',
    )

    current_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='ارزش روز',
    )
    last_valuation_date = models.DateField(
        null=True, blank=True, verbose_name='تاریخ آخرین قیمت‌گذاری'
    )

    cabinet_number = models.CharField(
        max_length=50, blank=True, default='', verbose_name='شماره کمد'
    )
    drawer_number = models.CharField(
        max_length=50, blank=True, default='', verbose_name='شماره کشو'
    )
    box_number = models.CharField(
        max_length=50, blank=True, default='', verbose_name='شماره باکس'
    )

    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مدال'
        verbose_name_plural = 'مدال‌ها'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country', 'year']),
            models.Index(fields=['catalog_number']),
            models.Index(fields=['quality']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        year_part = f' ({self.year})' if self.year else ''
        return f'{self.name}{year_part}'


from .related_models import (  # noqa: E402
    medal_image_upload_to,
    medal_file_upload_to,
    MedalImageType,
    MedalFileType,
    MedalImage,
    MedalFile,
    MedalPurchaseRecord,
    MedalValuationRecord,
)
