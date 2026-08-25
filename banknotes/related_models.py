from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


def banknotes_image_upload_to(instance, filename):
    return f'banknotes/{instance.item_id}/images/{filename}'


class BanknoteImageType(models.TextChoices):
    FRONT = 'front', 'رو'
    BACK = 'back', 'پشت'
    DETAIL = 'detail', 'جزئیات'
    CERTIFICATE = 'certificate', 'گواهی'
    OTHER = 'other', 'سایر'


class BanknoteImage(models.Model):
    item = models.ForeignKey(
        'banknotes.Banknote', on_delete=models.CASCADE, related_name='images', verbose_name='اسکناس'
    )
    image = models.ImageField(upload_to=banknotes_image_upload_to, verbose_name='تصویر')
    image_type = models.CharField(
        max_length=20, choices=BanknoteImageType.choices, default=BanknoteImageType.OTHER, verbose_name='نوع تصویر'
    )
    caption = models.CharField(max_length=255, blank=True, default='', verbose_name='عنوان')
    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_primary = models.BooleanField(default=False, db_index=True, verbose_name='تصویر اصلی')
    original_filename = models.CharField(max_length=255, blank=True, default='', verbose_name='نام فایل اصلی')
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='حجم فایل')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='uploaded_banknotes_images', verbose_name='آپلودکننده',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = 'تصویر اسکناس'
        verbose_name_plural = 'تصاویر اسکناس‌ها'

    def __str__(self):
        return f'{self.item_id}:{self.image_type}:{self.pk}'


class BanknotePurchaseRecord(models.Model):
    item = models.ForeignKey(
        'banknotes.Banknote', on_delete=models.CASCADE, related_name='purchase_records', verbose_name='اسکناس'
    )
    purchase_date = models.DateField(null=True, blank=True, verbose_name='تاریخ خرید')
    location = models.CharField(max_length=255, blank=True, default='', verbose_name='محل خرید')
    seller = models.CharField(max_length=150, blank=True, default='', verbose_name='فروشنده')
    price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], verbose_name='قیمت',
    )
    currency = models.CharField(max_length=10, blank=True, default='', verbose_name='واحد پول')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_banknotes_purchases', verbose_name='ایجادکننده',
    )

    class Meta:
        ordering = ['-purchase_date', '-id']
        verbose_name = 'سابقه خرید اسکناس'
        verbose_name_plural = 'سوابق خرید اسکناس‌ها'

    def __str__(self):
        return f'Purchase {self.pk} for banknotes {self.item_id}'


class BanknoteValuationRecord(models.Model):
    item = models.ForeignKey(
        'banknotes.Banknote', on_delete=models.CASCADE, related_name='valuation_records', verbose_name='اسکناس'
    )
    value = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='ارزش',
    )
    currency = models.CharField(max_length=10, blank=True, default='', verbose_name='واحد پول')
    valuation_date = models.DateField(verbose_name='تاریخ قیمت‌گذاری')
    source = models.CharField(max_length=255, blank=True, default='', verbose_name='منبع')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_banknotes_valuations', verbose_name='ایجادکننده',
    )

    class Meta:
        ordering = ['-valuation_date', '-id']
        verbose_name = 'سابقه ارزش‌گذاری اسکناس'
        verbose_name_plural = 'سوابق ارزش‌گذاری اسکناس‌ها'

    def __str__(self):
        return f'Valuation {self.pk} for banknotes {self.item_id}'
