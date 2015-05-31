import os

import django
from django.test import TestCase

from term_market.solver import solver


class SolverTestCase(TestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def setUp(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")
        django.setup()

    def test_solve_cycles(self):
        # given
        cycles = os.path.join(self.BASE_DIR, 'tests/static/cycles.json')
        collisions = os.path.join(self.BASE_DIR, 'tests/static/collisions.json')
        s = solver.Solver(cycles, collisions)

        # when
        best, list_of_cycles = s.solve()

        # then
        self.assertEqual(s.offers[1].id, 1)
        self.assertEqual(s.offers[1].donor, 1)
        self.assertEqual(s.offers[1].offered_term, 1)