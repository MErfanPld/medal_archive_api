"""
Import sample medals into the database.

Usage (from project root, with venv active):
    python manage.py seed_sample_medals
    python manage.py seed_sample_medals --dry-run
    python manage.py seed_sample_medals --update   # update existing by catalog_number
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from categories.models import Category
from medals.models import AuthenticityStatus, CurrencyCode, Medal, QualityGrade


# ---------------------------------------------------------------------------
# Helpers: map free-text Persian/English labels to model choice codes
# ---------------------------------------------------------------------------

QUALITY_MAP = {
    "UNC": QualityGrade.UNC,
    "AU": QualityGrade.AU,
    "XF": QualityGrade.XF,
    "VF": QualityGrade.VF,
    "F": QualityGrade.F,
    "VG": QualityGrade.VG,
    "G": QualityGrade.G,
    "AG": QualityGrade.AG,
    "FAIR": QualityGrade.FAIR,
    "POOR": QualityGrade.POOR,
    "بسیار عالی": QualityGrade.XF,
    "عالی": QualityGrade.AU,
    "خوب": QualityGrade.VF,
    "متوسط": QualityGrade.F,
}

AUTH_MAP = {
    "اصلی": AuthenticityStatus.AUTHENTIC,
    "authentic": AuthenticityStatus.AUTHENTIC,
    "مشکوک": AuthenticityStatus.SUSPECT,
    "suspect": AuthenticityStatus.SUSPECT,
    "جعلی": AuthenticityStatus.COUNTERFEIT,
    "تأییدنشده": AuthenticityStatus.UNVERIFIED,
    "تاییدنشده": AuthenticityStatus.UNVERIFIED,
    "unverified": AuthenticityStatus.UNVERIFIED,
    "نامشخص": AuthenticityStatus.UNKNOWN,
}


def map_quality(raw: str | None) -> str:
    if not raw:
        return ""
    raw = raw.strip()
    # e.g. "XF — بسیار عالی" or "AU"
    key = raw.split()[0].replace("—", "").replace("-", "").strip()
    if key in QUALITY_MAP:
        return QUALITY_MAP[key]
    for k, v in QUALITY_MAP.items():
        if k in raw:
            return v
    return QualityGrade.OTHER


def map_auth(raw: str | None) -> str:
    if not raw:
        return AuthenticityStatus.UNKNOWN
    raw = raw.strip()
    if raw in AUTH_MAP:
        return AUTH_MAP[raw]
    for k, v in AUTH_MAP.items():
        if k in raw:
            return v
    return AuthenticityStatus.UNKNOWN


def D(value) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# Dataset — edit / append freely; unique key is catalog_number
# ---------------------------------------------------------------------------

MEDALS: list[dict] = [
    # ---- 1. مدال‌های افتخار ----
    {
        "category_name": "مدال‌های افتخار",
        "name": "نشان شیر و خورشید درجه اول",
        "country": "ایران",
        "year": 1873,
        "catalog_number": "IR-HON-1873-001",
        "occasion": "اعطای نشان افتخار سلطنتی",
        "historical_period": "قاجار",
        "material": "طلا",
        "weight": "42.8",
        "diameter": "58",
        "thickness": "3.2",
        "shape": "ستاره",
        "color": "طلایی",
        "edge": "ساده",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه سلطنتی تهران",
        "mint_or_manufacturer": "ضرابخانه سلطنتی تهران",
        "authenticity": "اصلی",
        "purchase_date": date(2019, 7, 9),  # ۱۳۹۸/۰۴/۱۸
        "purchase_location": "تهران، بازار بزرگ",
        "seller": "مجموعه‌دار خصوصی",
        "purchase_price": "185000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "420000000",
        "last_valuation_date": date(2026, 6, 2),  # ۱۴۰۵/۰۳/۱۲
        "cabinet_number": "A",
        "drawer_number": "02",
        "box_number": "BX-018",
        "notes": "نمونه آرشیوی مربوط به دوره ناصرالدین‌شاه.",
    },
    {
        "category_name": "مدال‌های افتخار",
        "name": "نشان همایون",
        "country": "ایران",
        "year": 1930,
        "catalog_number": "IR-HON-1930-002",
        "occasion": "اعطای نشان سلطنتی",
        "historical_period": "پهلوی",
        "material": "نقره با روکش طلا",
        "weight": "36.5",
        "diameter": "52",
        "shape": "ستاره",
        "color": "طلایی",
        "quality": "AU",
        "preservation_condition": "عالی",
        "maker": "کارگاه سلطنتی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "اصلی",
        "purchase_location": "تهران",
        "seller": "حراجی آثار تاریخی",
        "purchase_price": "125000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "280000000",
        "cabinet_number": "A",
        "drawer_number": "02",
        "box_number": "BX-021",
    },
    {
        "category_name": "مدال‌های افتخار",
        "name": "نشان افتخار خدمات دولتی",
        "country": "ایران",
        "year": 1942,
        "catalog_number": "IR-HON-1942-003",
        "occasion": "تقدیر از خدمات اداری",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "28.4",
        "diameter": "45",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "VF",
        "preservation_condition": "خوب",
        "maker": "کارگاه مدال‌سازی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "اصفهان",
        "seller": "مجموعه‌دار",
        "purchase_price": "24000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "65000000",
        "cabinet_number": "A",
        "drawer_number": "03",
        "box_number": "BX-027",
    },
    # ---- 2. مدال‌های المپیک ----
    {
        "category_name": "مدال‌های المپیک",
        "name": "مدال برنز المپیک لندن ۱۹۴۸",
        "country": "بریتانیا",
        "year": 1948,
        "catalog_number": "OLY-LON-1948-BR-001",
        "occasion": "بازی‌های المپیک لندن",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "70.2",
        "diameter": "60",
        "thickness": "4.5",
        "shape": "گرد",
        "color": "برنزی",
        "edge": "ساده",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "Royal Mint",
        "mint_or_manufacturer": "Royal Mint, London",
        "authenticity": "اصلی",
        "purchase_date": date(2021, 9, 13),  # ۱۴۰۰/۰۶/۲۲
        "purchase_location": "لندن",
        "seller": "Olympic Memorabilia Dealer",
        "purchase_price": "320000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "850000000",
        "cabinet_number": "B",
        "drawer_number": "01",
        "box_number": "OLY-001",
    },
    {
        "category_name": "مدال‌های المپیک",
        "name": "مدال طلای المپیک ملبورن ۱۹۵۶",
        "country": "استرالیا",
        "year": 1956,
        "catalog_number": "OLY-MEL-1956-GO-002",
        "occasion": "بازی‌های المپیک ملبورن",
        "historical_period": "پهلوی",
        "material": "نقره با روکش طلا",
        "weight": "71.0",
        "diameter": "68",
        "thickness": "5",
        "shape": "گرد",
        "color": "طلایی",
        "edge": "ساده",
        "quality": "AU",
        "preservation_condition": "عالی",
        "maker": "Royal Australian Mint",
        "mint_or_manufacturer": "Melbourne",
        "authenticity": "اصلی",
        "purchase_location": "ملبورن",
        "seller": "Olympic Collector",
        "purchase_price": "680000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "1750000000",
        "cabinet_number": "B",
        "drawer_number": "01",
        "box_number": "OLY-004",
    },
    {
        "category_name": "مدال‌های المپیک",
        "name": "مدال طلای المپیک توکیو ۱۹۶۴",
        "country": "ژاپن",
        "year": 1964,
        "catalog_number": "OLY-TOK-1964-GO-003",
        "occasion": "بازی‌های المپیک توکیو",
        "historical_period": "پهلوی",
        "material": "نقره با روکش طلا",
        "weight": "90.1",
        "diameter": "60",
        "thickness": "4.8",
        "shape": "گرد",
        "color": "طلایی",
        "edge": "ساده",
        "quality": "UNC",
        "preservation_condition": "عالی",
        "maker": "Japan Mint",
        "mint_or_manufacturer": "Osaka",
        "authenticity": "اصلی",
        "purchase_location": "توکیو",
        "seller": "Tokyo Medal Gallery",
        "purchase_price": "590000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "1350000000",
        "cabinet_number": "B",
        "drawer_number": "02",
        "box_number": "OLY-007",
    },
    # ---- 3. مدال‌های تاریخی ----
    {
        "category_name": "مدال‌های تاریخی",
        "name": "مدال یادبود ناصرالدین‌شاه",
        "country": "ایران",
        "year": 1896,
        "catalog_number": "IR-HIS-1896-001",
        "occasion": "یادبود سلطنت ناصرالدین‌شاه",
        "historical_period": "قاجار",
        "material": "برنز",
        "weight": "92.5",
        "diameter": "63",
        "thickness": "5.2",
        "shape": "گرد",
        "color": "برنزی",
        "edge": "حروف‌دار",
        "quality": "VF",
        "preservation_condition": "خوب",
        "maker": "کارگاه سلطنتی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "اصلی",
        "purchase_location": "تهران",
        "seller": "مجموعه‌دار خصوصی",
        "purchase_price": "45000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "120000000",
        "cabinet_number": "C",
        "drawer_number": "01",
        "box_number": "HIS-001",
    },
    {
        "category_name": "مدال‌های تاریخی",
        "name": "مدال یادبود افتتاح راه‌آهن",
        "country": "ایران",
        "year": 1938,
        "catalog_number": "IR-HIS-1938-002",
        "occasion": "یادبود افتتاح راه‌آهن سراسری ایران",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "76.3",
        "diameter": "58",
        "shape": "گرد",
        "color": "برنزی",
        "edge": "حروف‌دار",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه مدال‌سازی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "تهران",
        "seller": "بازار عتیقه",
        "purchase_price": "38000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "110000000",
        "cabinet_number": "C",
        "drawer_number": "02",
        "box_number": "HIS-005",
    },
    {
        "category_name": "مدال‌های تاریخی",
        "name": "مدال یادبود جشن‌های سلطنتی",
        "country": "ایران",
        "year": 1967,
        "catalog_number": "IR-HIS-1967-003",
        "occasion": "جشن‌های سلطنتی",
        "historical_period": "پهلوی",
        "material": "نقره",
        "weight": "81.7",
        "diameter": "55",
        "shape": "گرد",
        "color": "نقره‌ای",
        "quality": "UNC",
        "preservation_condition": "عالی",
        "maker": "کارخانه ضرب سکه و مدال تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "اصلی",
        "purchase_location": "شیراز",
        "seller": "حراجی آثار تاریخی",
        "purchase_price": "85000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "240000000",
        "cabinet_number": "C",
        "drawer_number": "03",
        "box_number": "HIS-009",
    },
    # ---- 4. مدال‌های نظامی ----
    {
        "category_name": "مدال‌های نظامی",
        "name": "نشان ذوالفقار",
        "country": "ایران",
        "year": 1937,
        "catalog_number": "IR-MIL-1937-001",
        "occasion": "تقدیر از شجاعت نظامی",
        "historical_period": "پهلوی",
        "material": "طلا",
        "weight": "47.6",
        "diameter": "61",
        "shape": "ستاره",
        "color": "طلایی",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه سلطنتی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "مشکوک",
        "purchase_location": "تهران",
        "seller": "مجموعه‌دار نظامی",
        "purchase_price": "210000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "520000000",
        "cabinet_number": "D",
        "drawer_number": "01",
        "box_number": "MIL-001",
    },
    {
        "category_name": "مدال‌های نظامی",
        "name": "نشان شیر و خورشید نظامی",
        "country": "ایران",
        "year": 1902,
        "catalog_number": "IR-MIL-1902-002",
        "occasion": "خدمات نظامی",
        "historical_period": "قاجار",
        "material": "نقره",
        "weight": "34.8",
        "diameter": "49",
        "shape": "صلیب",
        "color": "نقره‌ای",
        "quality": "VF",
        "preservation_condition": "خوب",
        "maker": "کارگاه سلطنتی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "اصلی",
        "purchase_location": "تبریز",
        "seller": "کلکسیونر خصوصی",
        "purchase_price": "95000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "230000000",
        "cabinet_number": "D",
        "drawer_number": "02",
        "box_number": "MIL-006",
    },
    {
        "category_name": "مدال‌های نظامی",
        "name": "نشان خدمت ارتش شاهنشاهی",
        "country": "ایران",
        "year": 1955,
        "catalog_number": "IR-MIL-1955-003",
        "occasion": "خدمت طولانی‌مدت در ارتش",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "31.2",
        "diameter": "44",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "AU",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه مدال‌سازی ارتش",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "تهران",
        "seller": "بازار مجموعه‌داران",
        "purchase_price": "32000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "87000000",
        "cabinet_number": "D",
        "drawer_number": "03",
        "box_number": "MIL-011",
    },
    # ---- 5. مدال‌های ورزشی ----
    {
        "category_name": "مدال‌های ورزشی",
        "name": "قهرمانی کشتی",
        "country": "ایران",
        "year": 1959,
        "catalog_number": "IR-SPT-1959-001",
        "occasion": "مسابقات کشتی",
        "historical_period": "پهلوی",
        "material": "نقره",
        "weight": "63.4",
        "diameter": "52",
        "shape": "گرد",
        "color": "نقره‌ای",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه مدال‌سازی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "تهران",
        "seller": "مجموعه‌دار ورزشی",
        "purchase_price": "28000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "75000000",
        "cabinet_number": "E",
        "drawer_number": "01",
        "box_number": "SPT-001",
    },
    {
        "category_name": "مدال‌های ورزشی",
        "name": "قهرمانی وزنه‌برداری",
        "country": "ایران",
        "year": 1965,
        "catalog_number": "IR-SPT-1965-002",
        "occasion": "مسابقات وزنه‌برداری",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "58.9",
        "diameter": "50",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "VF",
        "preservation_condition": "خوب",
        "maker": "کارگاه ورزشی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "اصلی",
        "purchase_location": "اصفهان",
        "seller": "کلکسیونر",
        "purchase_price": "18000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "52000000",
        "cabinet_number": "E",
        "drawer_number": "02",
        "box_number": "SPT-005",
    },
    {
        "category_name": "مدال‌های ورزشی",
        "name": "قهرمانی دو و میدانی",
        "country": "فرانسه",
        "year": 1935,
        "catalog_number": "FR-SPT-1935-003",
        "occasion": "مسابقات دو و میدانی",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "44.6",
        "diameter": "48",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "VF",
        "preservation_condition": "متوسط",
        "maker": "Paris Medal Works",
        "mint_or_manufacturer": "پاریس",
        "authenticity": "اصلی",
        "purchase_location": "پاریس",
        "seller": "French Sports Collectibles",
        "purchase_price": "15000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "46000000",
        "cabinet_number": "E",
        "drawer_number": "03",
        "box_number": "SPT-008",
    },
    # ---- 6. مسابقات ملی ----
    {
        "category_name": "مسابقات ملی",
        "name": "قهرمانی ملی کشتی ایران",
        "country": "ایران",
        "year": 1949,  # ۱۳۲۸ شمسی
        "catalog_number": "IR-NAT-1949-001",
        "occasion": "مسابقات قهرمانی کشور",
        "historical_period": "پهلوی",
        "material": "نقره",
        "weight": "54.2",
        "diameter": "51",
        "thickness": "3",
        "shape": "گرد",
        "color": "نقره‌ای",
        "edge": "ساده",
        "quality": "VF",
        "preservation_condition": "خوب",
        "maker": "کارگاه مدال‌سازی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "تهران",
        "seller": "مجموعه‌دار",
        "purchase_price": "22000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "68000000",
        "cabinet_number": "F",
        "drawer_number": "01",
        "box_number": "NAT-001",
    },
    {
        "category_name": "مسابقات ملی",
        "name": "قهرمانی ملی دو و میدانی",
        "country": "ایران",
        "year": 1963,  # ۱۳۴۲
        "catalog_number": "IR-NAT-1963-002",
        "occasion": "مسابقات قهرمانی کشور",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "46.8",
        "diameter": "49",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "XF",
        "preservation_condition": "بسیار خوب",
        "maker": "کارگاه ورزشی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "مشهد",
        "seller": "مجموعه‌دار ورزشی",
        "purchase_price": "17000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "49000000",
        "cabinet_number": "F",
        "drawer_number": "02",
        "box_number": "NAT-006",
    },
    {
        "category_name": "مسابقات ملی",
        "name": "قهرمانی ملی ژیمناستیک",
        "country": "ایران",
        "year": 1973,  # ۱۳۵۲
        "catalog_number": "IR-NAT-1973-003",
        "occasion": "مسابقات قهرمانی کشور",
        "historical_period": "پهلوی",
        "material": "برنز",
        "weight": "41.3",
        "diameter": "47",
        "shape": "گرد",
        "color": "برنزی",
        "quality": "AU",
        "preservation_condition": "عالی",
        "maker": "کارگاه مدال‌سازی تهران",
        "mint_or_manufacturer": "تهران",
        "authenticity": "تأییدنشده",
        "purchase_location": "تهران",
        "seller": "حراجی ورزشی",
        "purchase_price": "19000000",
        "purchase_currency": CurrencyCode.IRR,
        "current_value": "58000000",
        "cabinet_number": "F",
        "drawer_number": "03",
        "box_number": "NAT-011",
    },
]


class Command(BaseCommand):
    help = "Seed sample medals and categories into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and print actions without writing to DB.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="If catalog_number already exists, update fields instead of skipping.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        do_update = options["update"]
        created_n = updated_n = skipped_n = 0
        category_cache: dict[str, Category] = {}

        def get_category(name: str) -> Category | None:
            if name in category_cache:
                return category_cache[name]
            if dry_run:
                cat = Category.objects.filter(name=name).first()
                category_cache[name] = cat
                return cat
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": f"دسته‌بندی {name}", "is_active": True},
            )
            category_cache[name] = cat
            return cat

        with transaction.atomic():
            for row in MEDALS:
                data = dict(row)
                cat_name = data.pop("category_name")
                catalog = data.get("catalog_number") or ""
                quality_raw = data.pop("quality", "")
                auth_raw = data.pop("authenticity", "")
                data["quality"] = map_quality(quality_raw)
                data["authenticity"] = map_auth(auth_raw)
                data["weight"] = D(data.get("weight"))
                data["diameter"] = D(data.get("diameter"))
                data["thickness"] = D(data.get("thickness"))
                data["purchase_price"] = D(data.get("purchase_price"))
                data["current_value"] = D(data.get("current_value"))
                for f in (
                    "country", "occasion", "historical_period", "maker",
                    "mint_or_manufacturer", "material", "shape", "color", "edge",
                    "preservation_condition", "catalog_number", "purchase_location",
                    "seller", "purchase_currency", "cabinet_number",
                    "drawer_number", "box_number", "notes",
                ):
                    data.setdefault(f, "")
                    if data[f] is None:
                        data[f] = ""

                category = get_category(cat_name)
                data["category"] = category

                existing = (
                    Medal.objects.filter(catalog_number=catalog).first()
                    if catalog
                    else None
                )

                if existing and not do_update:
                    self.stdout.write(f"  skip  {catalog}  ({existing.name})")
                    skipped_n += 1
                    continue

                if dry_run:
                    action = "UPDATE" if existing else "CREATE"
                    self.stdout.write(
                        f"  {action}  {catalog}  {data['name']}  [{cat_name}]"
                    )
                    if existing:
                        updated_n += 1
                    else:
                        created_n += 1
                    continue

                if existing and do_update:
                    for k, v in data.items():
                        setattr(existing, k, v)
                    existing.save()
                    self.stdout.write(self.style.WARNING(f"  update {catalog}  {existing.name}"))
                    updated_n += 1
                else:
                    medal = Medal.objects.create(**data)
                    self.stdout.write(self.style.SUCCESS(f"  create {catalog}  {medal.name}"))
                    created_n += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created_n}  updated={updated_n}  skipped={skipped_n}"
                + ("  (dry-run)" if dry_run else "")
            )
        )
