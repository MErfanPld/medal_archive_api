import io
from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from categories.models import Category
from users.models import User, Role, Permission, UserRole, RolePermission
from users.permission_catalog import PERMISSIONS, DEFAULT_ROLES, ROLE_CURATOR, ROLE_VIEWER

from .models import Medal, MedalImage, MedalPurchaseRecord


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


def tiny_png(name='test.png'):
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (1, 1), color=(255, 0, 0)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


def sample_pdf(name='doc.pdf'):
    return SimpleUploadedFile(name, b'%PDF-1.4\n%%EOF\n', content_type='application/pdf')


class MedalAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(
            username='root', password='RootPass123!'
        )
        self.curator = User.objects.create_user(
            username='curator', password='CuratorPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser
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
        self.category = Category.objects.create(name='Military', slug='military')
        self.list_url = reverse('medals:medal-list')

    def _payload(self, **overrides):
        data = {
            'name': 'Order of the Lion',
            'country': 'Iran',
            'year': 1925,
            'category': self.category.pk,
            'material': 'gold',
            'weight': '12.500',
            'diameter': '30.00',
            'quality': 'XF',
        }
        data.update(overrides)
        return data

    def test_unauthenticated_401(self):
        self.assertEqual(
            self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_without_permission_403(self):
        self.client.force_authenticate(user=self.plain)
        self.assertEqual(
            self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN
        )

    def test_viewer_can_list_not_create(self):
        Medal.objects.create(name='Sample', country='Iran')
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        resp = self.client.post(self.list_url, self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_curator_crud(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        medal_id = resp.data['id']
        detail = reverse('medals:medal-detail', kwargs={'pk': medal_id})
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
        resp = self.client.patch(detail, {'notes': 'Restored'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_can_create(self):
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.post(self.list_url, self._payload(name='Royal Medal'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_negative_weight_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(weight='-1'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_price_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(
            self.list_url, self._payload(purchase_price='-10'), format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_year_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(year=5000), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_name_required(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.list_url, self._payload(name=''), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination(self):
        self.client.force_authenticate(user=self.viewer)
        for i in range(25):
            Medal.objects.create(name=f'Medal {i}')
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(resp.data['results']), 20)

    def test_list_select_related_no_error(self):
        Medal.objects.create(name='With Cat', category=self.category)
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = next(r for r in resp.data['results'] if r['name'] == 'With Cat')
        self.assertEqual(item['category_detail']['name'], 'Military')


class MedalSearchFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(
            username='root2', password='RootPass123!'
        )
        self.viewer = User.objects.create_user(
            username='viewer2', password='ViewerPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser
        )
        self.list_url = reverse('medals:medal-list')
        Medal.objects.create(
            name='Order of the Lion', country='Iran', year=1925,
            material='gold', weight=Decimal('12.5'), diameter=Decimal('30'), quality='XF',
        )
        Medal.objects.create(
            name='Silver Coin', country='Turkey', year=1910,
            material='silver', weight=Decimal('8'), diameter=Decimal('25'),
        )

    def test_filter_country_and_ranges(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.list_url, {
            'country': 'Iran', 'year_min': 1900, 'year_max': 1950,
            'weight_min': 10, 'diameter_min': 20, 'search': 'Lion', 'ordering': 'year',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_pagination_combined(self):
        self.client.force_authenticate(user=self.viewer)
        for i in range(25):
            Medal.objects.create(name=f'Extra {i}')
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(resp.data['results']), 20)


@override_settings(MEDIA_ROOT='/tmp/medal_test_media_fix')
class MedalImageFileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(
            username='root3', password='RootPass123!'
        )
        self.curator = User.objects.create_user(
            username='curator3', password='CuratorPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser
        )
        self.viewer = User.objects.create_user(
            username='viewer3', password='ViewerPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser
        )
        self.medal = Medal.objects.create(name='Img Medal', country='Iran', year=1930)

    def images_url(self):
        return reverse('medals:medal-image-list', kwargs={'medal_pk': self.medal.pk})

    def files_url(self):
        return reverse('medals:medal-file-list', kwargs={'medal_pk': self.medal.pk})

    def test_upload_list_max_images(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(
            self.images_url(),
            {'image': tiny_png(), 'image_type': 'front', 'is_primary': True},
            format='multipart',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        for i in range(9):
            r = self.client.post(
                self.images_url(),
                {'image': tiny_png(f't{i}.png'), 'image_type': 'other'},
                format='multipart',
            )
            self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        r = self.client.post(
            self.images_url(),
            {'image': tiny_png('overflow.png')},
            format='multipart',
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get(self.images_url()).data['count'], 10)

    def test_viewer_cannot_upload_image(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.post(
            self.images_url(),
            {'image': tiny_png(), 'image_type': 'front'},
            format='multipart',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_image_extension(self):
        self.client.force_authenticate(user=self.curator)
        bad = SimpleUploadedFile('x.exe', b'MZ', content_type='application/octet-stream')
        resp = self.client.post(self.images_url(), {'image': bad}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_image(self):
        self.client.force_authenticate(user=self.curator)
        img = MedalImage.objects.create(
            medal=self.medal, image=tiny_png(), image_type='front'
        )
        url = reverse(
            'medals:medal-image-detail',
            kwargs={'medal_pk': self.medal.pk, 'pk': img.pk},
        )
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)

    def test_upload_pdf_and_reject_exe(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(
            self.files_url(),
            {'file': sample_pdf(), 'file_type': 'certificate'},
            format='multipart',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        bad = SimpleUploadedFile('virus.exe', b'MZ\x90', content_type='application/octet-stream')
        resp = self.client.post(
            self.files_url(), {'file': bad, 'file_type': 'other'}, format='multipart'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_viewer_cannot_upload_file(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.post(
            self.files_url(),
            {'file': sample_pdf(), 'file_type': 'document'},
            format='multipart',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class PurchaseValuationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.roles = seed_catalog()
        self.superuser = User.objects.create_superuser(
            username='root4', password='RootPass123!'
        )
        self.curator = User.objects.create_user(
            username='curator4', password='CuratorPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.curator, role=self.roles[ROLE_CURATOR], assigned_by=self.superuser
        )
        self.viewer = User.objects.create_user(
            username='viewer4', password='ViewerPass1!', is_active=True
        )
        UserRole.objects.create(
            user=self.viewer, role=self.roles[ROLE_VIEWER], assigned_by=self.superuser
        )
        self.medal = Medal.objects.create(name='Val Medal', country='Iran', year=1940)

    def purchases_url(self):
        return reverse('medals:medal-purchase-list', kwargs={'medal_pk': self.medal.pk})

    def valuations_url(self):
        return reverse('medals:medal-valuation-list', kwargs={'medal_pk': self.medal.pk})

    def test_purchase_history(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(
            self.purchases_url(),
            {
                'purchase_date': '2020-01-15',
                'location': 'Tehran',
                'seller': 'Gallery A',
                'price': '100.00',
                'currency': 'USD',
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        resp = self.client.get(self.purchases_url())
        self.assertEqual(resp.data['count'], 1)

    def test_valuation_updates_snapshot(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(
            self.valuations_url(),
            {
                'value': '250.00',
                'currency': 'USD',
                'valuation_date': str(date.today()),
                'source': 'Expert',
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.medal.refresh_from_db()
        self.assertEqual(self.medal.current_value, Decimal('250.00'))
        self.assertEqual(self.medal.last_valuation_date, date.today())

    def test_viewer_can_list_not_create_purchase(self):
        MedalPurchaseRecord.objects.create(
            medal=self.medal, seller='X', price=Decimal('10')
        )
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(
            self.client.get(self.purchases_url()).status_code, status.HTTP_200_OK
        )
        resp = self.client.post(self.purchases_url(), {'seller': 'Y'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_negative_purchase_price_rejected(self):
        self.client.force_authenticate(user=self.curator)
        resp = self.client.post(self.purchases_url(), {'price': '-1'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
