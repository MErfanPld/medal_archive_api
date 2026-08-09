"""Database-backed collection analytics (no currency conversion)."""

from __future__ import annotations

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import TruncYear

from medals.models import Medal
from medals.related_models import MedalPurchaseRecord, MedalValuationRecord


def dashboard_summary() -> dict:
    base = Medal.objects.all()
    agg = base.aggregate(
        total_medals=Count('id'),
        countries=Count('country', distinct=True, filter=~Q(country='')),
        oldest_year=Min('year'),
        newest_year=Max('year'),
    )

    value_by_currency = []
    for row in (
        base.exclude(current_value__isnull=True)
        .values('purchase_currency')
        .annotate(
            total=Sum('current_value'),
            average=Avg('current_value'),
            count=Count('id'),
        )
        .order_by('-total')
    ):
        cur = (row['purchase_currency'] or '').strip() or 'UNSPECIFIED'
        value_by_currency.append({
            'currency': cur,
            'total': row['total'],
            'average': row['average'],
            'count': row['count'],
        })

    by_category = list(
        base.values('category_id', 'category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    by_country = list(
        base.exclude(country='')
        .values('country')
        .annotate(count=Count('id'))
        .order_by('-count')[:20]
    )

    return {
        'total_medals': agg['total_medals'] or 0,
        'countries': agg['countries'] or 0,
        'oldest_year': agg['oldest_year'],
        'newest_year': agg['newest_year'],
        'value_by_currency': value_by_currency,
        'medals_by_category': [
            {
                'category_id': r['category_id'],
                'category_name': r['category__name'] or 'بدون دسته',
                'count': r['count'],
            }
            for r in by_category
        ],
        'medals_by_country_top': [
            {'country': r['country'], 'count': r['count']} for r in by_country
        ],
    }


def country_report(*, limit: int | None = None) -> dict:
    total = Medal.objects.count()
    qs = (
        Medal.objects.exclude(country='')
        .values('country')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    if limit:
        qs = qs[: int(limit)]
    rows = list(qs)
    denom = total if total else 1
    items = [
        {
            'country': r['country'],
            'count': r['count'],
            'percentage': round(100.0 * r['count'] / denom, 2),
        }
        for r in rows
    ]
    return {'total_medals': total, 'items': items}


def value_report() -> dict:
    """Collection value analytics grouped by currency (no conversion)."""
    by_currency = []
    for row in (
        Medal.objects.exclude(current_value__isnull=True)
        .values('purchase_currency')
        .annotate(
            total=Sum('current_value'),
            average=Avg('current_value'),
            count=Count('id'),
        )
        .order_by('-total')
    ):
        by_currency.append({
            'currency': (row['purchase_currency'] or '').strip() or 'UNSPECIFIED',
            'total': row['total'],
            'average': row['average'],
            'count': row['count'],
        })

    by_country = []
    for row in (
        Medal.objects.exclude(current_value__isnull=True)
        .exclude(country='')
        .values('country', 'purchase_currency')
        .annotate(total=Sum('current_value'), count=Count('id'))
        .order_by('-total')[:50]
    ):
        by_country.append({
            'country': row['country'],
            'currency': (row['purchase_currency'] or '').strip() or 'UNSPECIFIED',
            'total': row['total'],
            'count': row['count'],
        })

    by_category = []
    for row in (
        Medal.objects.exclude(current_value__isnull=True)
        .values('category_id', 'category__name', 'purchase_currency')
        .annotate(total=Sum('current_value'), count=Count('id'))
        .order_by('-total')
    ):
        by_category.append({
            'category_id': row['category_id'],
            'category_name': row['category__name'] or 'بدون دسته',
            'currency': (row['purchase_currency'] or '').strip() or 'UNSPECIFIED',
            'total': row['total'],
            'count': row['count'],
        })

    over_time = []
    for row in (
        MedalValuationRecord.objects.exclude(value__isnull=True)
        .annotate(year=TruncYear('valuation_date'))
        .values('year', 'currency')
        .annotate(total=Sum('value'), count=Count('id'), average=Avg('value'))
        .order_by('year')
    ):
        year = row['year'].year if row['year'] else None
        over_time.append({
            'year': year,
            'currency': (row['currency'] or '').strip() or 'UNSPECIFIED',
            'total': row['total'],
            'average': row['average'],
            'count': row['count'],
        })

    return {
        'by_currency': by_currency,
        'by_country': by_country,
        'by_category': by_category,
        'over_time': over_time,
        'note': (
            'Currencies are never mixed. Totals are grouped by currency. '
            'No automatic FX conversion is applied.'
        ),
    }


def purchase_report() -> dict:
    """Purchase analytics from MedalPurchaseRecord."""
    records = MedalPurchaseRecord.objects.all()

    by_year = []
    for row in (
        records.exclude(purchase_date__isnull=True)
        .annotate(year=TruncYear('purchase_date'))
        .values('year', 'currency')
        .annotate(
            total_cost=Sum('price'),
            count=Count('id'),
            average=Avg('price'),
        )
        .order_by('year')
    ):
        by_year.append({
            'year': row['year'].year if row['year'] else None,
            'currency': (row['currency'] or '').strip() or 'UNSPECIFIED',
            'total_cost': row['total_cost'],
            'average': row['average'],
            'count': row['count'],
        })

    by_currency = []
    for row in (
        records.exclude(price__isnull=True)
        .values('currency')
        .annotate(total_cost=Sum('price'), count=Count('id'), average=Avg('price'))
        .order_by('-total_cost')
    ):
        by_currency.append({
            'currency': (row['currency'] or '').strip() or 'UNSPECIFIED',
            'total_cost': row['total_cost'],
            'average': row['average'],
            'count': row['count'],
        })

    by_seller = []
    for row in (
        records.exclude(seller='')
        .values('seller', 'currency')
        .annotate(total_cost=Sum('price'), count=Count('id'))
        .order_by('-count')[:30]
    ):
        by_seller.append({
            'seller': row['seller'],
            'currency': (row['currency'] or '').strip() or 'UNSPECIFIED',
            'total_cost': row['total_cost'],
            'count': row['count'],
        })

    by_country = []
    for row in (
        records.select_related('medal')
        .exclude(medal__country='')
        .values('medal__country', 'currency')
        .annotate(total_cost=Sum('price'), count=Count('id'))
        .order_by('-count')[:30]
    ):
        by_country.append({
            'country': row['medal__country'],
            'currency': (row['currency'] or '').strip() or 'UNSPECIFIED',
            'total_cost': row['total_cost'],
            'count': row['count'],
        })

    return {
        'purchase_count': records.count(),
        'by_year': by_year,
        'by_currency': by_currency,
        'by_seller': by_seller,
        'by_country': by_country,
        'note': 'Purchase totals are grouped by currency. No FX conversion.',
    }
