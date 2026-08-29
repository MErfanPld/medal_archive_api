from django.test import TestCase
from .models import Stamp


class StampModelTests(TestCase):
    def test_create(self):
        obj = Stamp.objects.create(name='نمونه تمبر')
        self.assertEqual(str(obj), 'نمونه تمبر')
