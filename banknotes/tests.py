from django.test import TestCase
from .models import Banknote


class BanknoteModelTests(TestCase):
    def test_create(self):
        obj = Banknote.objects.create(name='نمونه اسکناس')
        self.assertEqual(str(obj), 'نمونه اسکناس')
