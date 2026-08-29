from django.test import TestCase
from .models import Tasbih


class TasbihModelTests(TestCase):
    def test_create(self):
        obj = Tasbih.objects.create(name='نمونه تسبیح')
        self.assertEqual(str(obj), 'نمونه تسبیح')
