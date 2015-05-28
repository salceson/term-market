import os

import django
from django.test import TestCase

from term_market.solver import solver


class SolverTestCase(TestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def setUp(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")
        django.setup()

    def test_load_file(self):
        # given
        file1 = os.path.join(self.BASE_DIR, 'tests/static/file1.json')
        file2 = os.path.join(self.BASE_DIR, 'tests/static/file2.json')

        # when
        s = solver.Solver(file1, file2)

        # then
        self.assertEqual(s.offers[0].id, 1)
        self.assertEqual(s.offers[0].donor_id, 1)
        self.assertEqual(s.offers[0].offered_term_id, 1)
