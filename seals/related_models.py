from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


def seals_image_upload_to(instance, filename):
    return f'seals/{instance.item_id}/{filename}'


class SealImageType(models.TextChoices):
    FRONT = 'front', 'رو'
    BACK = 'back', 'پشت'
    DETAIL = 'detail', 'جزئیات'
    OTHER = 'other', 'سایر'


class SealImage(models.Model):
    item = models.ForeignKey(
        'seals.Seal', on_delete=models.CASCADE, related_name='images',
        verbose_name='مهر',
    )
    image = models.ImageField(upload_to=seals_image_upload_to, verbose_name='تصویر')
    image_type = models.CharField(
        max_length=20, choices=SealImageType.choices, default=SealImageType.OTHER,
        verbose_name='نوع تصویر',
    )
    caption = models.CharField(max_length=255, blank=True, default='', verbose_name='توضیح')
    is_primary = models.BooleanField(default=False, verbose_name='اصلی')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'تصویر مهر'
        verbose_name_plural = 'تصاویر مهر'

    def __str__(self):
        return f'{self.get_image_type_display()} - {self.item_id}'


class SealPurchaseRecord(models.Model):
    item = models.ForeignKey(
        'seals.Seal', on_delete=models.CASCADE, related_name='purchase_records',
        verbose_name='مهر',
    )
    purchase_date = models.DateField(null=True, blank=True, verbose_name='تاریخ خرید')
    purchase_location = models.CharField(max_length=255, blank=True, default='', verbose_name='محل خرید')
    seller = models.CharField(max_length=150, blank=True, default='', verbose_name='فروشنده')
    price = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], verbose_name='قیمت',
    )
    currency = models.CharField(max_length=10, blank=True, default='', verbose_name='واحد پول')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='seals_purchase_records', verbose_name='ایجادکننده',
    )

    class Meta:
        ordering = ['-purchase_date', '-id']
        verbose_name = 'سابقه خرید مهر'
        verbose_name_plural = 'سوابق خرید مهر'

    def __str__(self):
        return f'Purchase {self.pk} for seals {self.item_id}'


class SealValuationRecord(models.Model):
    item = models.ForeignKey(
        'seals.Seal', on_delete=models.CASCADE, related_name='valuation_records',
        verbose_name='مهر',
    )
    valuation_date = models.DateField(null=True, blank=True, verbose_name='تاریخ ارزیابی')
    value = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], verbose_name='ارزش',
    )
    currency = models.CharField(max_length=10, blank=True, default='', verbose_name='واحد پول')
    appraiser = models.CharField(max_length=150, blank=True, default='', verbose_name='ارزیاب')
    notes = models.TextField(blank=True, default='', verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='seals_valuation_records', verbose_name='ایجادکننده',
    )

    class Meta:
        ordering = ['-valuation_date', '-id']
        verbose_name = 'سابقه ارزیابی مهر'
        verbose_name_plural = 'سوابق ارزیابی مهر'

    def __str__(self):
        return f'Valuation {self.pk} for seals {self.item_id}'
