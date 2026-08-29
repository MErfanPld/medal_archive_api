from django.test import TestCase
from .models import Knife


class KnifeModelTests(TestCase):
    def test_create(self):
        obj = Knife.objects.create(name='نمونه چاقو')
        self.assertEqual(str(obj), 'نمونه چاقو')
