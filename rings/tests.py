from django.test import TestCase
from .models import Ring


class RingModelTests(TestCase):
    def test_create(self):
        obj = Ring.objects.create(name='نمونه انگشتر')
        self.assertEqual(str(obj), 'نمونه انگشتر')
