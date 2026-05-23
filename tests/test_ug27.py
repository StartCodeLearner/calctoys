"""Unit tests for ASME BPVC Div 1 UG-27 cylindrical shell calculations."""
import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


def make_calcs(**overrides):
    defaults = dict(
        inside_diameter=24.0,
        internal_pressure=100.0,
        allowable_stress=20000.0,
        joint_efficiency_long=1.0,
        joint_efficiency_circ=1.0,
        thickness=1.0,
    )
    defaults.update(overrides)
    return UG27Calcs(UG27params(**defaults))


class TestDesignThickness:
    def test_circ_stress_governs_for_typical_vessel(self):
        c = make_calcs()
        # t = PR / (SE - 0.6P) = 100*12 / (20000*1 - 60) = 1200/19940
        expected = 100 * 12 / (20000 * 1.0 - 0.6 * 100)
        assert math.isclose(c.design_thickness(), expected, rel_tol=1e-9)

    def test_design_thickness_increases_with_pressure(self):
        t_low = make_calcs(internal_pressure=100).design_thickness()
        t_high = make_calcs(internal_pressure=200).design_thickness()
        assert t_high > t_low

    def test_design_thickness_decreases_with_higher_allowable_stress(self):
        t_low_s = make_calcs(allowable_stress=15000).design_thickness()
        t_high_s = make_calcs(allowable_stress=20000).design_thickness()
        assert t_high_s < t_low_s

    def test_design_thickness_increases_with_larger_diameter(self):
        t_small = make_calcs(inside_diameter=12).design_thickness()
        t_large = make_calcs(inside_diameter=24).design_thickness()
        assert t_large > t_small

    def test_design_thickness_decreases_with_joint_efficiency_one(self):
        t_partial = make_calcs(joint_efficiency_long=0.85).design_thickness()
        t_full = make_calcs(joint_efficiency_long=1.0).design_thickness()
        assert t_full < t_partial


class TestMinThkCircStress:
    def test_formula_matches_ug27_circumferential(self):
        c = make_calcs(inside_diameter=20.0, internal_pressure=150.0,
                       allowable_stress=17500.0, joint_efficiency_long=0.85)
        R = 10.0
        P = 150.0
        S = 17500.0
        E = 0.85
        expected = P * R / (S * E - 0.6 * P)
        assert math.isclose(c.min_thk_circ_stress(), expected, rel_tol=1e-9)

    def test_zero_pressure_gives_zero_thickness(self):
        c = make_calcs(internal_pressure=0.0)
        assert c.min_thk_circ_stress() == 0.0


class TestMinThkLongitudinalStress:
    def test_formula_matches_ug27_longitudinal(self):
        c = make_calcs(inside_diameter=20.0, internal_pressure=150.0,
                       allowable_stress=17500.0, joint_efficiency_long=0.85)
        R = 10.0
        P = 150.0
        S = 17500.0
        E = 0.85
        expected = P * R / (2 * S * E + 0.4 * P)
        assert math.isclose(c.min_thk_longitudinal_stress(), expected, rel_tol=1e-9)

    def test_longitudinal_less_than_circ_for_typical_vessel(self):
        c = make_calcs()
        assert c.min_thk_longitudinal_stress() < c.min_thk_circ_stress()


class TestMaxPressure:
    def test_mawp_governed_by_circ_stress(self):
        c = make_calcs()
        # P = SEt / (R + 0.6t)
        R = 12.0
        S = 20000.0
        E = 1.0
        t = 1.0
        expected_circ = S * E * t / (R + 0.6 * t)
        assert math.isclose(c.max_pressure_circ_stress(), expected_circ, rel_tol=1e-9)

    def test_mawp_increases_with_thickness(self):
        c_thin = make_calcs(thickness=0.5)
        c_thick = make_calcs(thickness=1.5)
        assert c_thick.max_pressure() > c_thin.max_pressure()

    def test_mawp_consistency_with_design_thickness(self):
        # If we use the design thickness, MAWP should be >= the design pressure.
        design_pressure = 250.0
        c = make_calcs(internal_pressure=design_pressure)
        t_min = c.design_thickness()
        c2 = make_calcs(internal_pressure=design_pressure, thickness=t_min)
        assert c2.max_pressure() >= design_pressure - 1e-6

    def test_mawp_is_minimum_of_two_modes(self):
        c = make_calcs()
        assert c.max_pressure() == min(c.max_pressure_circ_stress(),
                                       c.max_pressure_longitudinal_stress())
