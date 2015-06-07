import os

import django
from django.test import TestCase

from term_market.solver import offers_solver


class SolverTestCase(TestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def setUp(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TermMarket.settings")
        django.setup()

    def test_solve_cycles(self):
        # given
        cycles = os.path.join(self.BASE_DIR, 'tests/static/offers1.json')
        collisions = os.path.join(self.BASE_DIR, 'tests/static/collisions1.json')
        s = offers_solver.Solver(cycles, collisions, 'output1.csv')

        # when
        list_of_cycles = s.solve()

        # then
        self.assertEqual(s.offers[1].id, 1)
        self.assertEqual(s.offers[1].donor, 1)
        self.assertEqual(s.offers[1].offered_term, 1)
        self.assertEqual(list_of_cycles, [[2, 1, 3]])

    def test_solve_collisions(self):
        # given
        cycles = os.path.join(self.BASE_DIR, 'tests/static/offers2.json')
        collisions = os.path.join(self.BASE_DIR, 'tests/static/collisions2.json')
        s = offers_solver.Solver(cycles, collisions, 'output2.csv')

        # when
        list_of_cycles = s.solve()

        # then
        self.assertEqual(list_of_cycles, [[2, 1, 3]])
