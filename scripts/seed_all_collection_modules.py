#!/usr/bin/env python
"""
Seed fake data for seals, tasbih, rings, knives, antiques, stamps.

Run from project root:
  python scripts/seed_all_collection_modules.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root must be on sys.path when invoked as scripts/...
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from decimal import Decimal
from django.db import transaction
from categories.models import Category

def D(v):
    if v is None or v == "":
        return None
    return Decimal(str(v))

def get_cat(name):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"is_active": True})
    return cat

def seed_seals():
    from seals.models import Seal, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="مهر ناصرالدین‌شاه", seal_type="رسمی سلطنتی", owner_name="ناصرالدین‌شاه", title_or_rank="شاهنشاه", inscription="ناصر الدین شاه قاجار", script="نستعلیق", material="عقیق", shape="بیضی", dimensions="۳×۲.۵", weight=D("18.5"), country="ایران", year=1870, historical_period="قاجار", catalog_number="IR-SEAL-1870-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("95000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("280000000"), cabinet_number="S", drawer_number="01", box_number="SEAL-001"),
        dict(name="مهر مظفرالدین‌شاه", seal_type="رسمی", owner_name="مظفرالدین‌شاه", material="یشم", shape="مربع", country="ایران", year=1905, historical_period="قاجار", catalog_number="IR-SEAL-1905-002", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("72000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("195000000"), cabinet_number="S", drawer_number="01", box_number="SEAL-004"),
        dict(name="مهر امیرکبیر", seal_type="شخصی", owner_name="میرزا تقی‌خان", title_or_rank="امیرکبیر", material="عقیق سرخ", country="ایران", year=1850, historical_period="قاجار", catalog_number="IR-SEAL-1850-AMK", condition=ConditionGrade.FAIR, authenticity=AuthenticityStatus.UNVERIFIED, purchase_price=D("45000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("120000000"), cabinet_number="S", drawer_number="02", box_number="SEAL-010"),
        dict(name="مهر طغرای عثمانی", seal_type="رسمی دولتی", owner_name="عبدالحمید دوم", material="برنز", shape="گرد", country="امپراتوری عثمانی", year=1890, historical_period="عثمانی", catalog_number="OT-SEAL-1890-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("38000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("95000000"), cabinet_number="S", drawer_number="03", box_number="SEAL-OT-1"),
    ]
    cat = get_cat("مهرهای قاجار")
    n = 0
    for s in samples:
        if Seal.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Seal.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

def seed_tasbih():
    from tasbih.models import Tasbih, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="تسبیح عقیق یمنی ۳۳ دانه", bead_material="عقیق یمنی", bead_count=33, bead_size=D("8"), color="قرمز تیره", weight=D("42.5"), is_natural=True, country="یمن", year=1980, catalog_number="TB-AGATE-033-001", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("18500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("42000000"), cabinet_number="T", drawer_number="01", box_number="TB-001"),
        dict(name="تسبیح کهربای بالتیک ۹۹ دانه", bead_material="کهربا", bead_count=99, bead_size=D("6"), color="عسلی", weight=D("38"), is_natural=True, country="لیتوانی", year=1995, catalog_number="TB-AMB-099-001", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("65000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("145000000"), cabinet_number="T", drawer_number="02", box_number="TB-008"),
        dict(name="تسبیح یشم سبز ۳۳ دانه", bead_material="یشم", bead_count=33, color="سبز", weight=D("55.2"), is_natural=True, country="چین", year=1970, catalog_number="TB-JADE-033-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.UNVERIFIED, purchase_price=D("28000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("62000000"), cabinet_number="T", drawer_number="01", box_number="TB-012"),
        dict(name="تسبیح چوب صندل ۹۹ دانه", bead_material="چوب صندل", bead_count=99, color="قهوه‌ای", weight=D("25"), is_natural=True, country="هند", year=2005, catalog_number="TB-WOOD-099-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("4500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("12000000"), cabinet_number="T", drawer_number="03", box_number="TB-020"),
    ]
    cat = get_cat("تسبیح")
    n = 0
    for s in samples:
        if Tasbih.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Tasbih.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

def seed_rings():
    from rings.models import Ring, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="انگشتر عقیق یمنی یا علی", metal="نقره", purity="925", stone_type="عقیق یمنی", stone_color="قرمز", stone_weight=D("3.2"), ring_size="21", weight=D("8.5"), style="ایرانی", engraving="یا علی", is_set=True, country="ایران", year=1960, catalog_number="IR-RING-AGATE-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("12500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("38000000"), cabinet_number="R", drawer_number="01", box_number="RING-001"),
        dict(name="انگشتر فیروزه نیشابور", metal="نقره", purity="925", stone_type="فیروزه", stone_color="آبی", stone_weight=D("2.8"), ring_size="20", weight=D("7.2"), is_set=True, country="ایران", year=1975, catalog_number="IR-RING-TURQ-002", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("22000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("65000000"), cabinet_number="R", drawer_number="01", box_number="RING-005"),
        dict(name="انگشتر طلای مردانه", metal="طلا", purity="18", ring_size="22", weight=D("6.1"), is_set=False, country="ایران", year=2000, catalog_number="IR-RING-GOLD-003", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("85000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("210000000"), cabinet_number="R", drawer_number="02", box_number="RING-010"),
        dict(name="انگشتر یاقوت سرخ", metal="طلا", purity="18", stone_type="یاقوت", stone_color="سرخ", stone_weight=D("1.5"), ring_size="17", weight=D("5.8"), is_set=True, country="میانمار", year=1985, catalog_number="MM-RING-RUBY-001", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.UNVERIFIED, purchase_price=D("320000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("780000000"), cabinet_number="R", drawer_number="03", box_number="RING-015"),
    ]
    cat = get_cat("انگشتر")
    n = 0
    for s in samples:
        if Ring.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Ring.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

def seed_knives():
    from knives.models import Knife, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="چاقوی سنتی زنجان دسته شاخ", knife_type="چاقوی سنتی", blade_material="فولاد کربنی", blade_length=D("12"), total_length=D("22"), handle_material="شاخ گوزن", origin_region="زنجان", weight=D("180"), has_sheath=True, country="ایران", year=1970, catalog_number="IR-KNIFE-ZAN-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("8500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("28000000"), cabinet_number="K", drawer_number="01", box_number="KN-001"),
        dict(name="کارد آشپزخانه زنجان", knife_type="کارد آشپزخانه", blade_material="فولاد ضدزنگ", blade_length=D("18"), total_length=D("30"), handle_material="چوب گردو", origin_region="زنجان", weight=D("220"), has_sheath=False, country="ایران", year=1990, catalog_number="IR-KNIFE-ZAN-002", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("4200000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("11000000"), cabinet_number="K", drawer_number="01", box_number="KN-005"),
        dict(name="خنجر کردی غلاف نقره", knife_type="خنجر", blade_material="فولاد دمشق", blade_length=D("25"), total_length=D("40"), handle_material="استخوان", sheath_material="نقره", origin_region="کردستان", weight=D("450"), has_sheath=True, country="ایران", year=1950, catalog_number="IR-DAGGER-KURD-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.UNVERIFIED, purchase_price=D("55000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("145000000"), cabinet_number="K", drawer_number="02", box_number="KN-010"),
        dict(name="چاقوی جیبی وینتیج سوئیسی", knife_type="چاقوی جیبی", blade_material="فولاد ضدزنگ", blade_length=D("7"), total_length=D("16"), handle_material="آلومینیوم", maker="Victorinox", origin_region="سوئیس", weight=D("55"), has_sheath=False, country="سوئیس", year=1985, catalog_number="CH-KNIFE-VICT-001", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("9500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("22000000"), cabinet_number="K", drawer_number="03", box_number="KN-015"),
    ]
    cat = get_cat("چاقو")
    n = 0
    for s in samples:
        if Knife.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Knife.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

def seed_antiques():
    from antiques.models import Antique, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="سینی مسی قلم‌زنی اصفهان", object_type="سینی", material="مس", style_period="قاجار", dimensions="۴۵ سانتی‌متر", weight=D("1200"), technique="قلم‌زنی", country="ایران", year=1880, historical_period="قاجار", catalog_number="IR-ANT-COPPER-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("35000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("95000000"), cabinet_number="A", drawer_number="01", box_number="ANT-001"),
        dict(name="کوزه سفالی نیشابور", object_type="کوزه", material="سفال", style_period="سلجوقی", dimensions="ارتفاع ۲۵", weight=D("800"), technique="لعاب آبی", country="ایران", year=1200, historical_period="سلجوقی", catalog_number="IR-ANT-POT-002", condition=ConditionGrade.FAIR, authenticity=AuthenticityStatus.UNVERIFIED, purchase_price=D("48000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("135000000"), cabinet_number="A", drawer_number="02", box_number="ANT-008"),
        dict(name="جعبه منبت‌کاری شیراز", object_type="جعبه", material="چوب گردو", style_period="قاجار", dimensions="۳۰×۲۰×۱۵", weight=D("950"), technique="منبت", country="ایران", year=1900, historical_period="قاجار", catalog_number="IR-ANT-WOOD-003", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("22000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("58000000"), cabinet_number="A", drawer_number="03", box_number="ANT-012"),
        dict(name="قوری برنزی قاجاری", object_type="قوری", material="برنز", style_period="قاجار", dimensions="ارتفاع ۱۸", weight=D("650"), technique="ریخته‌گری", country="ایران", year=1875, historical_period="قاجار", catalog_number="IR-ANT-BRONZE-004", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("28000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("72000000"), cabinet_number="A", drawer_number="01", box_number="ANT-015"),
    ]
    cat = get_cat("آنتیک")
    n = 0
    for s in samples:
        if Antique.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Antique.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

def seed_stamps():
    from stamps.models import Stamp, AuthenticityStatus, ConditionGrade, PurchaseCurrency
    samples = [
        dict(name="تمبر شیر و خورشید ۱ شاهی", face_value=D("1"), denomination="شاهی", issue_name="سری شیر و خورشید", color="قرمز", is_used=False, is_mint=True, theme="نماد ملی", country="ایران", year=1870, historical_period="قاجار", catalog_number="IR-STAMP-1870-001", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("15000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("48000000"), cabinet_number="ST", drawer_number="01", box_number="STAMP-001"),
        dict(name="تمبر تاجگذاری محمدرضا شاه", face_value=D("10"), denomination="ریال", issue_name="یادبود تاجگذاری", color="طلایی و آبی", is_used=False, is_mint=True, theme="تاجگذاری", country="ایران", year=1967, historical_period="پهلوی", catalog_number="IR-STAMP-1967-COR", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("8500000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("25000000"), cabinet_number="ST", drawer_number="02", box_number="STAMP-010"),
        dict(name="تمبر نوروز ۱۳۵۰", face_value=D("2"), denomination="ریال", issue_name="نوروز", color="سبز", is_used=True, is_mint=False, theme="نوروز", country="ایران", year=1971, historical_period="پهلوی", catalog_number="IR-STAMP-1971-NOW", condition=ConditionGrade.GOOD, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("1200000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("4500000"), cabinet_number="ST", drawer_number="02", box_number="STAMP-015"),
        dict(name="تمبر یادبود پنی سیاه بریتانیا", face_value=D("1"), denomination="penny", issue_name="Penny Black commemorative", color="سیاه", is_used=False, is_mint=True, theme="تاریخی", country="بریتانیا", year=1990, catalog_number="GB-STAMP-PENNY-REP", condition=ConditionGrade.EXCELLENT, authenticity=AuthenticityStatus.AUTHENTIC, purchase_price=D("5000000"), purchase_currency=PurchaseCurrency.IRR, current_value=D("12000000"), cabinet_number="ST", drawer_number="03", box_number="STAMP-UK-1", notes="نسخه یادبود؛ نه اصل ۱۸۴۰."),
    ]
    cat = get_cat("تمبر")
    n = 0
    for s in samples:
        if Stamp.objects.filter(catalog_number=s["catalog_number"]).exists():
            print("  skip", s["catalog_number"]); continue
        Stamp.objects.create(category=cat, **s)
        print("  create", s["catalog_number"]); n += 1
    return n

if __name__ == "__main__":
    with transaction.atomic():
        print("=== seals ==="); a = seed_seals()
        print("=== tasbih ==="); b = seed_tasbih()
        print("=== rings ==="); c = seed_rings()
        print("=== knives ==="); d = seed_knives()
        print("=== antiques ==="); e = seed_antiques()
        print("=== stamps ==="); f = seed_stamps()
    print(f"Done. seals={a} tasbih={b} rings={c} knives={d} antiques={e} stamps={f}")
