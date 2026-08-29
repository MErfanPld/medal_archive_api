from django.test import TestCase
from .models import Antique


class AntiqueModelTests(TestCase):
    def test_create(self):
        obj = Antique.objects.create(name='نمونه آنتیک')
        self.assertEqual(str(obj), 'نمونه آنتیک')
