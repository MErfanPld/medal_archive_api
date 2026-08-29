from django.test import TestCase
from .models import Seal


class SealModelTests(TestCase):
    def test_create(self):
        obj = Seal.objects.create(name='نمونه مهر')
        self.assertEqual(str(obj), 'نمونه مهر')
