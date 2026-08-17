"""
Seed realistic sample coins and banknotes.

Usage:
  python manage.py seed_sample_coins
  python manage.py seed_sample_coins --update
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from categories.models import Category
from coins.models import AuthenticityStatus, Coin, ItemType, PurchaseCurrency, QualityGrade


SAMPLES = [
    # --- سکه‌های قاجار ---
    {
        "category_name": "سکه‌های قاجار",
        "name": "سکه طلای دو تومانی ناصرالدین‌شاه",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1875,
        "year_hijri": 1292,
        "historical_period": "قاجار",
        "reign_or_ruler": "ناصرالدین‌شاه",
        "face_value": "2",
        "denomination": "تومان",
        "currency_name": "تومان قاجار",
        "material": "طلا",
        "purity": "90",
        "weight": "3.4",
        "diameter": "20",
        "shape": "گرد",
        "edge": "دندانه‌دار",
        "catalog_number": "IR-COIN-1875-001",
        "quality": QualityGrade.XF,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "ضرابخانه تهران",
        "is_commemorative": False,
        "purchase_price": "85000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "220000000",
        "cabinet_number": "G",
        "drawer_number": "01",
        "box_number": "COIN-001",
        "notes": "نمونه با نقش شیر و خورشید.",
    },
    {
        "category_name": "سکه‌های قاجار",
        "name": "قران نقره مظفرالدین‌شاه",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1902,
        "year_hijri": 1320,
        "historical_period": "قاجار",
        "reign_or_ruler": "مظفرالدین‌شاه",
        "face_value": "1",
        "denomination": "قران",
        "material": "نقره",
        "purity": "90",
        "weight": "4.6",
        "diameter": "23",
        "catalog_number": "IR-COIN-1902-002",
        "quality": QualityGrade.VF,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "تهران",
        "purchase_price": "18000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "52000000",
        "cabinet_number": "G",
        "drawer_number": "01",
        "box_number": "COIN-004",
    },
    {
        "category_name": "سکه‌های قاجار",
        "name": "سکه پنجاه دینار مسی",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1890,
        "historical_period": "قاجار",
        "reign_or_ruler": "ناصرالدین‌شاه",
        "face_value": "50",
        "denomination": "دینار",
        "material": "مس",
        "weight": "5.2",
        "diameter": "26",
        "catalog_number": "IR-COIN-1890-050",
        "quality": QualityGrade.F,
        "authenticity": AuthenticityStatus.UNVERIFIED,
        "mint": "تبریز",
        "purchase_price": "3500000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "12000000",
        "cabinet_number": "G",
        "drawer_number": "02",
        "box_number": "COIN-009",
    },
    # --- سکه‌های پهلوی ---
    {
        "category_name": "سکه‌های پهلوی",
        "name": "سکه پنج ریالی پهلوی",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1951,
        "year_hijri": 1330,
        "historical_period": "پهلوی",
        "reign_or_ruler": "محمدرضا شاه",
        "face_value": "5",
        "denomination": "ریال",
        "currency_name": "ریال ایران",
        "material": "مس-نیکل",
        "weight": "4.6",
        "diameter": "25",
        "catalog_number": "IR-COIN-1951-005",
        "quality": QualityGrade.VF,
        "authenticity": AuthenticityStatus.UNVERIFIED,
        "mint": "تهران",
        "purchase_price": "2500000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "8000000",
        "cabinet_number": "G",
        "drawer_number": "02",
        "box_number": "COIN-012",
    },
    {
        "category_name": "سکه‌های پهلوی",
        "name": "سکه طلای پهلوی یک پهلوی",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1975,
        "year_hijri": 1354,
        "historical_period": "پهلوی",
        "reign_or_ruler": "محمدرضا شاه",
        "face_value": "1",
        "denomination": "پهلوی",
        "material": "طلا",
        "purity": "90",
        "weight": "8.13",
        "diameter": "22",
        "catalog_number": "IR-COIN-1975-PAH",
        "quality": QualityGrade.AU,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "ضرابخانه تهران",
        "is_proof": False,
        "purchase_price": "420000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "980000000",
        "cabinet_number": "G",
        "drawer_number": "01",
        "box_number": "COIN-020",
        "notes": "سکه بانکی طلای پهلوی.",
    },
    {
        "category_name": "سکه‌های پهلوی",
        "name": "سکه ده ریالی یادبود تاجگذاری",
        "item_type": ItemType.COIN,
        "country": "ایران",
        "year": 1967,
        "historical_period": "پهلوی",
        "face_value": "10",
        "denomination": "ریال",
        "material": "مس-نیکل",
        "weight": "6.0",
        "diameter": "28",
        "catalog_number": "IR-COIN-1967-COR",
        "quality": QualityGrade.UNC,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "تهران",
        "is_commemorative": True,
        "purchase_price": "15000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "48000000",
        "cabinet_number": "G",
        "drawer_number": "03",
        "box_number": "COIN-025",
    },
    # --- اسکناس ---
    {
        "category_name": "اسکناس‌های پهلوی",
        "name": "اسکناس ۱۰۰ ریالی پهلوی",
        "item_type": ItemType.BANKNOTE,
        "country": "ایران",
        "year": 1961,
        "historical_period": "پهلوی",
        "reign_or_ruler": "محمدرضا شاه",
        "face_value": "100",
        "denomination": "ریال",
        "currency_name": "ریال ایران",
        "color": "سبز",
        "serial_number": "12/345678",
        "series": "سری دوم",
        "printer": "Thomas De La Rue",
        "catalog_number": "IR-NOTE-1961-100",
        "quality": QualityGrade.AU,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "purchase_price": "12000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "45000000",
        "cabinet_number": "H",
        "drawer_number": "01",
        "box_number": "NOTE-001",
    },
    {
        "category_name": "اسکناس‌های پهلوی",
        "name": "اسکناس ۵۰۰ ریالی پهلوی",
        "item_type": ItemType.BANKNOTE,
        "country": "ایران",
        "year": 1971,
        "historical_period": "پهلوی",
        "face_value": "500",
        "denomination": "ریال",
        "color": "قهوه‌ای",
        "serial_number": "45/987654",
        "series": "سری سوم",
        "printer": "Thomas De La Rue",
        "catalog_number": "IR-NOTE-1971-500",
        "quality": QualityGrade.XF,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "purchase_price": "28000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "95000000",
        "cabinet_number": "H",
        "drawer_number": "01",
        "box_number": "NOTE-008",
    },
    {
        "category_name": "اسکناس‌های پهلوی",
        "name": "اسکناس ۱۰۰۰ ریالی پهلوی",
        "item_type": ItemType.BANKNOTE,
        "country": "ایران",
        "year": 1974,
        "historical_period": "پهلوی",
        "face_value": "1000",
        "denomination": "ریال",
        "color": "بنفش",
        "serial_number": "78/112233",
        "series": "سری چهارم",
        "catalog_number": "IR-NOTE-1974-1000",
        "quality": QualityGrade.VF,
        "authenticity": AuthenticityStatus.UNVERIFIED,
        "purchase_price": "35000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "110000000",
        "cabinet_number": "H",
        "drawer_number": "02",
        "box_number": "NOTE-015",
    },
    # --- خارجی ---
    {
        "category_name": "سکه‌های خارجی",
        "name": "سکه یک دلاری آمریکا (Peace Dollar)",
        "item_type": ItemType.COIN,
        "country": "آمریکا",
        "year": 1923,
        "historical_period": "قرن بیستم",
        "face_value": "1",
        "denomination": "دلار",
        "currency_name": "USD",
        "material": "نقره",
        "purity": "90",
        "weight": "26.73",
        "diameter": "38.1",
        "catalog_number": "US-COIN-1923-PEACE",
        "quality": QualityGrade.AU,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "Philadelphia",
        "purchase_price": "95000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "210000000",
        "cabinet_number": "I",
        "drawer_number": "01",
        "box_number": "US-001",
    },
    {
        "category_name": "سکه‌های خارجی",
        "name": "سکه یک پوندی انگلیس",
        "item_type": ItemType.COIN,
        "country": "بریتانیا",
        "year": 1983,
        "face_value": "1",
        "denomination": "پوند",
        "currency_name": "GBP",
        "material": "نیکل-برنج",
        "weight": "9.5",
        "diameter": "22.5",
        "catalog_number": "UK-COIN-1983-1GBP",
        "quality": QualityGrade.UNC,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "mint": "Royal Mint",
        "purchase_price": "8000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "18000000",
        "cabinet_number": "I",
        "drawer_number": "02",
        "box_number": "UK-003",
    },
    {
        "category_name": "اسکناس‌های خارجی",
        "name": "اسکناس ۱۰ دلاری آمریکا",
        "item_type": ItemType.BANKNOTE,
        "country": "آمریکا",
        "year": 1950,
        "face_value": "10",
        "denomination": "دلار",
        "currency_name": "USD",
        "color": "سبز",
        "serial_number": "B12345678A",
        "series": "1950A",
        "catalog_number": "US-NOTE-1950-10",
        "quality": QualityGrade.VF,
        "authenticity": AuthenticityStatus.AUTHENTIC,
        "purchase_price": "42000000",
        "purchase_currency": PurchaseCurrency.IRR,
        "current_value": "88000000",
        "cabinet_number": "I",
        "drawer_number": "03",
        "box_number": "USN-002",
    },
]


class Command(BaseCommand):
    help = "Seed sample coins and banknotes with realistic Iranian and foreign items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing rows matched by catalog_number.",
        )

    def handle(self, *args, **options):
        do_update = options["update"]
        created = updated = skipped = 0
        with transaction.atomic():
            for row in SAMPLES:
                data = dict(row)
                cat_name = data.pop("category_name")
                cat, _ = Category.objects.get_or_create(
                    name=cat_name, defaults={"is_active": True}
                )
                catalog = data["catalog_number"]
                for key in (
                    "face_value", "purity", "weight", "diameter", "thickness",
                    "purchase_price", "current_value",
                ):
                    if key in data and data[key] is not None:
                        data[key] = Decimal(str(data[key]))

                existing = Coin.objects.filter(catalog_number=catalog).first()
                if existing and not do_update:
                    self.stdout.write(f"  skip  {catalog}")
                    skipped += 1
                    continue
                if existing and do_update:
                    for k, v in data.items():
                        setattr(existing, k, v)
                    existing.category = cat
                    existing.save()
                    self.stdout.write(self.style.WARNING(f"  update {catalog}"))
                    updated += 1
                else:
                    Coin.objects.create(category=cat, **data)
                    self.stdout.write(self.style.SUCCESS(f"  create {catalog}"))
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created} updated={updated} skipped={skipped}"
            )
        )
