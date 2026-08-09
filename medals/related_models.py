from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .models import CurrencyCode


def medal_image_upload_to(instance, filename):
    return f'medals/{instance.medal_id}/images/{filename}'


def medal_file_upload_to(instance, filename):
    return f'medals/{instance.medal_id}/files/{filename}'


class MedalImageType(models.TextChoices):
    FRONT = 'front', 'رو'
    BACK = 'back', 'پشت'
    EDGE = 'edge', 'لبه'
    PACKAGING = 'packaging', 'بسته‌بندی'
    CERTIFICATE = 'certificate', 'گواهی'
    INVOICE = 'invoice', 'فاکتور'
    OTHER = 'other', 'سایر'


class MedalFileType(models.TextChoices):
    CERTIFICATE = 'certificate', 'گواهی'
    INVOICE = 'invoice', 'فاکتور'
    DOCUMENT = 'document', 'سند'
    OTHER = 'other', 'سایر'


class MedalImage(models.Model):
    medal = models.ForeignKey('medals.Medal', on_delete=models.CASCADE, related_name='images', verbose_name='مدال')
    image = models.ImageField(upload_to=medal_image_upload_to, verbose_name='تصویر')
    image_type = models.CharField(max_length=20, choices=MedalImageType.choices, default=MedalImageType.OTHER, verbose_name='نوع تصویر')
    caption = models.CharField(max_length=255, blank=True, default='', verbose_name='عنوان')
    ordering = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_primary = models.BooleanField(default=False, db_index=True, verbose_name='تصویر اصلی')
    original_filename = models.CharField(max_length=255, blank=True, default='', verbose_name='نام فایل اصلی')
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='حجم فایل')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_medal_images', verbose_name='آپلودکننده')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = 'تصویر مدال'
        verbose_name_plural = 'تصاویر مدال'

    def __str__(self):
        return f'{self.medal_id}:{self.image_type}:{self.pk}'


class MedalFile(models.Model):
    medal = models.ForeignKey('medals.Medal', on_delete=models.CASCADE, related_name='files', verbose_name='مدال')
    file = models.FileField(upload_to=medal_file_upload_to, verbose_name='فایل')
    file_type = models.CharField(max_length=20, choices=MedalFileType.choices, default=MedalFileType.OTHER, verbose_name='نوع فایل')
    original_filename = models.CharField(max_length=255, blank=True, default='', verbose_name='نام فایل اصلی')
    content_type = models.CharField(max_length=100, blank=True, default='', verbose_name='نوع محتوا')
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='حجم فایل')
    notes = models.CharField(max_length=255, blank=True, default='', verbose_name='یادداشت')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_medal_files', verbose_name='آپلودکننده')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'فایل مدال'
        verbose_name_plural = 'فایل‌های مدال'

    def __str__(self):
        return f'{self.medal_id}:{self.file_type}:{self.original_filename}'


class MedalPurchaseRecord(models.Model):
    medal = models.ForeignKey('medals.Medal', on_delete=models.CASCADE, related_name='purchase_records', verbose_name='مدال')
    purchase_date = models.DateField(null=True, blank=True, verbose_name='تاریخ خرید')
    location = models.CharField(max_length=255, blank=True, default='', verbose_name='محل خرید')
    seller = models.CharField(max_length=150, blank=True, default='', verbose_name='فروشنده')
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='قیمت')
    currency = models.CharField(max_length=10, choices=CurrencyCode.choices, blank=True, default='', verbose_name='واحد پول')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_purchase_records', verbose_name='ایجادکننده')

    class Meta:
        ordering = ['-purchase_date', '-id']
        verbose_name = 'سوابق خرید'
        verbose_name_plural = 'سوابق خرید'

    def __str__(self):
        return f'Purchase {self.pk} for medal {self.medal_id}'


class MedalValuationRecord(models.Model):
    medal = models.ForeignKey('medals.Medal', on_delete=models.CASCADE, related_name='valuation_records', verbose_name='مدال')
    value = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='ارزش')
    currency = models.CharField(max_length=10, choices=CurrencyCode.choices, blank=True, default='', verbose_name='واحد پول')
    valuation_date = models.DateField(verbose_name='تاریخ قیمت‌گذاری')
    source = models.CharField(max_length=255, blank=True, default='', verbose_name='منبع')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_valuation_records', verbose_name='ایجادکننده')

    class Meta:
        ordering = ['-valuation_date', '-id']
        verbose_name = 'سوابق قیمت‌گذاری'
        verbose_name_plural = 'سوابق قیمت‌گذاری'

    def __str__(self):
        return f'Valuation {self.pk} for medal {self.medal_id}'
