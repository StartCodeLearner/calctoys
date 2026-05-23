import math
import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


class TestUG27CalcsDesignThickness(unittest.TestCase):
    def _make_calcs(self, D=24.0, P=100.0, S=20000.0, E_long=1.0, E_circ=1.0, t=1.0):
        params = UG27params(D, P, S, E_long, E_circ, t)
        return UG27Calcs(params)

    def test_design_thickness_governed_by_circ_stress(self):
        # For typical thin-wall, circumferential stress governs
        calcs = self._make_calcs(D=24.0, P=100.0, S=20000.0)
        t_circ = calcs.min_thk_circ_stress()
        t_long = calcs.min_thk_longitudinal_stress()
        self.assertAlmostEqual(calcs.design_thickness(), max(t_circ, t_long), places=10)

    def test_min_thk_circ_stress_formula(self):
        # t = P*R / (S*E - 0.6*P),  R = D/2
        calcs = self._make_calcs(D=24.0, P=100.0, S=20000.0, E_long=1.0)
        R = 12.0
        expected = 100.0 * R / (20000.0 * 1.0 - 0.6 * 100.0)
        self.assertAlmostEqual(calcs.min_thk_circ_stress(), expected, places=10)

    def test_min_thk_longitudinal_stress_formula(self):
        # t = P*R / (2*S*E + 0.4*P)
        calcs = self._make_calcs(D=24.0, P=100.0, S=20000.0, E_long=1.0)
        R = 12.0
        expected = 100.0 * R / (2 * 20000.0 * 1.0 + 0.4 * 100.0)
        self.assertAlmostEqual(calcs.min_thk_longitudinal_stress(), expected, places=10)

    def test_circ_stress_thk_greater_than_long_stress_thk(self):
        # Circumferential stress always produces a larger minimum thickness
        calcs = self._make_calcs()
        self.assertGreater(calcs.min_thk_circ_stress(), calcs.min_thk_longitudinal_stress())

    def test_design_thickness_equals_circ_stress_thk(self):
        calcs = self._make_calcs()
        self.assertAlmostEqual(calcs.design_thickness(), calcs.min_thk_circ_stress(), places=10)

    def test_max_pressure_circ_stress_formula(self):
        # P = S*E*t / (R + 0.6*t)
        calcs = self._make_calcs(D=24.0, S=20000.0, E_long=1.0, t=1.0)
        R = 12.0
        expected = 20000.0 * 1.0 * 1.0 / (R + 0.6 * 1.0)
        self.assertAlmostEqual(calcs.max_pressure_circ_stress(), expected, places=10)

    def test_max_pressure_longitudinal_stress_formula(self):
        # P = 2*S*E_circ*t / (R - 0.4*t)
        calcs = self._make_calcs(D=24.0, S=20000.0, E_long=1.0, E_circ=1.0, t=1.0)
        R = 12.0
        expected = 2 * 20000.0 * 1.0 * 1.0 / (R - 0.4 * 1.0)
        self.assertAlmostEqual(calcs.max_pressure_longitudinal_stress(), expected, places=10)

    def test_max_pressure_is_minimum_of_two_limits(self):
        calcs = self._make_calcs()
        expected = min(calcs.max_pressure_circ_stress(), calcs.max_pressure_longitudinal_stress())
        self.assertAlmostEqual(calcs.max_pressure(), expected, places=10)

    def test_joint_efficiency_reduces_allowable_pressure(self):
        calcs_full = self._make_calcs(E_long=1.0, E_circ=1.0)
        calcs_reduced = self._make_calcs(E_long=0.85, E_circ=0.85)
        self.assertGreater(calcs_full.max_pressure(), calcs_reduced.max_pressure())

    def test_larger_diameter_requires_greater_thickness(self):
        calcs_small = self._make_calcs(D=12.0)
        calcs_large = self._make_calcs(D=48.0)
        self.assertGreater(calcs_large.design_thickness(), calcs_small.design_thickness())

    def test_higher_pressure_requires_greater_thickness(self):
        calcs_low = self._make_calcs(P=50.0)
        calcs_high = self._make_calcs(P=500.0)
        self.assertGreater(calcs_high.design_thickness(), calcs_low.design_thickness())


if __name__ == '__main__':
    unittest.main()
