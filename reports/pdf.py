"""Server-side PDF report generation (reportlab)."""

from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from . import services


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=16, spaceAfter=12, leading=20))
    styles.add(ParagraphStyle(name='Section', fontSize=12, spaceBefore=10, spaceAfter=6, leading=16))
    styles.add(ParagraphStyle(name='BodyFa', fontSize=9, leading=12))
    return styles


def _header(story, styles, title: str):
    story.append(Paragraph(title, styles['ReportTitle']))
    story.append(Paragraph(
        f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}',
        styles['BodyFa'],
    ))
    story.append(Spacer(1, 0.4 * cm))


def _table(headers, rows, col_widths=None):
    data = [headers] + rows
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table


def build_pdf(report_type: str) -> bytes:
    """Return PDF bytes for the requested report type."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    styles = _styles()
    story = []

    if report_type == 'summary':
        data = services.dashboard_summary()
        _header(story, styles, 'Collection Summary Report')
        story.append(Paragraph(
            f"Total medals: {data['total_medals']} | "
            f"Countries: {data['countries']} | "
            f"Years: {data['oldest_year']} – {data['newest_year']}",
            styles['BodyFa'],
        ))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph('Value by currency', styles['Section']))
        rows = [
            [v['currency'], str(v['total']), str(v['average']), str(v['count'])]
            for v in data['value_by_currency']
        ]
        story.append(_table(['Currency', 'Total', 'Average', 'Count'], rows or [['—', '—', '—', '0']]))
        story.append(Paragraph('Medals by category', styles['Section']))
        rows = [
            [str(c['category_name']), str(c['count'])]
            for c in data['medals_by_category'][:40]
        ]
        story.append(_table(['Category', 'Count'], rows or [['—', '0']]))

    elif report_type == 'countries':
        data = services.country_report(limit=100)
        _header(story, styles, 'Country Distribution Report')
        rows = [
            [i['country'], str(i['count']), f"{i['percentage']}%"]
            for i in data['items']
        ]
        story.append(_table(['Country', 'Count', 'Percentage'], rows or [['—', '0', '0%']]))

    elif report_type == 'valuation':
        data = services.value_report()
        _header(story, styles, 'Valuation Report')
        story.append(Paragraph(data['note'], styles['BodyFa']))
        story.append(Paragraph('By currency', styles['Section']))
        rows = [
            [v['currency'], str(v['total']), str(v['average']), str(v['count'])]
            for v in data['by_currency']
        ]
        story.append(_table(['Currency', 'Total', 'Average', 'Count'], rows or [['—', '—', '—', '0']]))
        story.append(Paragraph('Over time (valuation history)', styles['Section']))
        rows = [
            [str(v['year']), v['currency'], str(v['total']), str(v['count'])]
            for v in data['over_time'][:80]
        ]
        story.append(_table(['Year', 'Currency', 'Total', 'Count'], rows or [['—', '—', '—', '0']]))

    elif report_type == 'purchases':
        data = services.purchase_report()
        _header(story, styles, 'Purchase Report')
        story.append(Paragraph(f"Purchase records: {data['purchase_count']}", styles['BodyFa']))
        story.append(Paragraph(data['note'], styles['BodyFa']))
        story.append(Paragraph('By currency', styles['Section']))
        rows = [
            [v['currency'], str(v['total_cost']), str(v['average']), str(v['count'])]
            for v in data['by_currency']
        ]
        story.append(_table(['Currency', 'Total cost', 'Average', 'Count'], rows or [['—', '—', '—', '0']]))
        story.append(Paragraph('By year', styles['Section']))
        rows = [
            [str(v['year']), v['currency'], str(v['total_cost']), str(v['count'])]
            for v in data['by_year'][:80]
        ]
        story.append(_table(['Year', 'Currency', 'Total cost', 'Count'], rows or [['—', '—', '—', '0']]))

    elif report_type == 'inventory':
        from medals.models import Medal
        _header(story, styles, 'Medal Inventory (first 200)')
        medals = (
            Medal.objects.select_related('category')
            .order_by('name')[:200]
            .values_list('id', 'name', 'country', 'year', 'category__name', 'catalog_number')
        )
        rows = [
            [str(m[0]), (m[1] or '')[:40], m[2] or '', str(m[3] or ''), (m[4] or '')[:20], m[5] or '']
            for m in medals
        ]
        story.append(_table(
            ['ID', 'Name', 'Country', 'Year', 'Category', 'Catalog'],
            rows or [['—'] * 6],
            col_widths=[1.2*cm, 5*cm, 2.5*cm, 1.5*cm, 3*cm, 2.5*cm],
        ))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph('Limited to 200 rows for PDF size safety.', styles['BodyFa']))

    else:
        raise ValueError(f'Unknown report type: {report_type}')

    doc.build(story)
    return buffer.getvalue()


ALLOWED_PDF_TYPES = frozenset({
    'summary', 'countries', 'valuation', 'purchases', 'inventory',
})
