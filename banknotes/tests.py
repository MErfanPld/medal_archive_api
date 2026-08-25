from django.test import TestCase


class BanknoteSmokeTests(TestCase):
    def test_app_label(self):
        self.assertEqual('banknotes', 'banknotes')
