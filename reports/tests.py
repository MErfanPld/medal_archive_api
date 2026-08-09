from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from medals.models import Medal
from medals.related_models import MedalPurchaseRecord, MedalValuationRecord
from users.models import User, Role, Permission, UserRole, RolePermission
from users.permission_catalog import PERMISSIONS, DEFAULT_ROLES, ROLE_VIEWER


def seed_catalog():
    perm_map = {}
    for codename, name, description in PERMISSIONS:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': name, 'description': description},
        )
        perm_map[codename] = perm
    roles = {}
    for codename, meta in DEFAULT_ROLES.items():
        role, _ = Role.objects.get_or_create(
            codename=codename,
            defaults={
                'name': meta['name'],
                'description': meta['description'],
                'is_active': True,
            },
        )
        for pcode in meta['permissions']:
            RolePermission.objects.get_or_create(role=role, permission=perm_map[pcode])
        roles[codename] = role
    return roles


class ReportsBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(
            username='root', password='RootPass123!'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='ViewerPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser
        )
        self.plain = User.objects.create_user(
            username='plain', password='PlainPass123!', is_active=True
        )
        self.cat = Category.objects.create(name='Military', slug='military')
        self.m1 = Medal.objects.create(
            name='Lion', country='Iran', year=1925, category=self.cat,
            current_value=Decimal('100.00'), purchase_currency='USD',
            purchase_price=Decimal('80.00'),
        )
        self.m2 = Medal.objects.create(
            name='Eagle', country='France', year=1900,
            current_value=Decimal('200.00'), purchase_currency='USD',
        )
        self.m3 = Medal.objects.create(
            name='Rial Medal', country='Iran', year=1950,
            current_value=Decimal('500000'), purchase_currency='IRR',
        )
        MedalPurchaseRecord.objects.create(
            medal=self.m1, purchase_date=date(2020, 1, 1),
            seller='Gallery A', price=Decimal('80.00'), currency='USD',
        )
        MedalPurchaseRecord.objects.create(
            medal=self.m2, purchase_date=date(2021, 6, 1),
            seller='Gallery B', price=Decimal('180.00'), currency='USD',
        )
        MedalValuationRecord.objects.create(
            medal=self.m1, value=Decimal('100.00'), currency='USD',
            valuation_date=date(2022, 1, 1), source='Expert',
        )


class DashboardTests(ReportsBase):
    def test_unauthenticated_401(self):
        self.assertEqual(self.client.get(reverse('reports:summary')).status_code, 401)

    def test_plain_403(self):
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(self.client.get(reverse('reports:summary')).status_code, 403)

    def test_summary_metrics(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(reverse('reports:summary'))
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data['total_medals'], 3)
        self.assertEqual(resp.data['countries'], 2)
        self.assertEqual(resp.data['oldest_year'], 1900)
        self.assertEqual(resp.data['newest_year'], 1950)
        currencies = {v['currency'] for v in resp.data['value_by_currency']}
        self.assertIn('USD', currencies)
        self.assertIn('IRR', currencies)


class CountryReportTests(ReportsBase):
    def test_countries_percentages(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(reverse('reports:countries'), {'limit': 10})
        self.assertEqual(resp.status_code, 200)
        countries = {i['country']: i for i in resp.data['items']}
        self.assertIn('Iran', countries)
        self.assertEqual(countries['Iran']['count'], 2)


class ValuePurchaseTests(ReportsBase):
    def test_value_report(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(reverse('reports:value'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('by_currency', resp.data)
        self.assertIn('over_time', resp.data)

    def test_purchase_report(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(reverse('reports:purchases'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['purchase_count'], 2)


class PdfTests(ReportsBase):
    def test_pdf_requires_auth(self):
        self.assertEqual(
            self.client.get(reverse('reports:pdf'), {'type': 'summary'}).status_code, 401
        )

    def test_pdf_forbidden(self):
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(
            self.client.get(reverse('reports:pdf'), {'type': 'summary'}).status_code, 403
        )

    def test_pdf_invalid_type(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(
            self.client.get(reverse('reports:pdf'), {'type': 'nope'}).status_code, 400
        )

    def test_pdf_summary_ok(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(reverse('reports:pdf'), {'type': 'summary'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertTrue(resp.content.startswith(b'%PDF'))


class MuseumDetailTests(ReportsBase):
    def test_museum_401(self):
        url = reverse('medals:medal-museum', kwargs={'pk': self.m1.pk})
        self.assertEqual(self.client.get(url).status_code, 401)

    def test_museum_complete(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse('medals:medal-museum', kwargs={'pk': self.m1.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, resp.data)
        for key in (
            'name', 'country', 'year', 'images', 'files',
            'purchase_records', 'valuation_records', 'category_detail',
        ):
            self.assertIn(key, resp.data)
        self.assertEqual(len(resp.data['purchase_records']), 1)
        self.assertEqual(len(resp.data['valuation_records']), 1)

    def test_museum_query_count(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse('medals:medal-museum', kwargs={'pk': self.m1.pk})
        self.client.get(url)
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertLessEqual(len(ctx), 25)
