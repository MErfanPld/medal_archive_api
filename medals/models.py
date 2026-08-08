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
    name = models.CharField(max_length=255, db_index=True)
    country = models.CharField(max_length=100, blank=True, default='', db_index=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    occasion = models.CharField(max_length=255, blank=True, default='')
    historical_period = models.CharField(max_length=150, blank=True, default='', db_index=True)
    maker = models.CharField(max_length=150, blank=True, default='')
    mint_or_manufacturer = models.CharField(max_length=150, blank=True, default='')
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medals',
    )

    material = models.CharField(max_length=100, blank=True, default='')
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Weight in grams',
    )
    diameter = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Diameter in millimeters',
    )
    thickness = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Thickness in millimeters',
    )
    shape = models.CharField(max_length=80, blank=True, default='')
    color = models.CharField(max_length=80, blank=True, default='')
    edge = models.CharField(max_length=80, blank=True, default='')

    quality = models.CharField(
        max_length=10, choices=QualityGrade.choices, blank=True, default='',
        db_index=True,
    )
    preservation_condition = models.CharField(max_length=255, blank=True, default='')
    authenticity = models.CharField(
        max_length=20,
        choices=AuthenticityStatus.choices,
        default=AuthenticityStatus.UNKNOWN,
        db_index=True,
    )
    catalog_number = models.CharField(max_length=100, blank=True, default='', db_index=True)

    purchase_date = models.DateField(null=True, blank=True)
    purchase_location = models.CharField(max_length=255, blank=True, default='')
    seller = models.CharField(max_length=150, blank=True, default='')
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    purchase_currency = models.CharField(
        max_length=10, choices=CurrencyCode.choices, blank=True, default='',
    )

    current_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    last_valuation_date = models.DateField(null=True, blank=True)

    cabinet_number = models.CharField(max_length=50, blank=True, default='')
    drawer_number = models.CharField(max_length=50, blank=True, default='')
    box_number = models.CharField(max_length=50, blank=True, default='')

    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medal'
        verbose_name_plural = 'Medals'
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
