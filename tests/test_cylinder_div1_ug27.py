import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


class TestUG27Calcs:
    def setup_method(self):
        self.params = UG27params(
            inside_diameter=24.0,
            internal_pressure=100.0,
            allowable_stress=20000.0,
            joint_efficiency_long=1.0,
            joint_efficiency_circ=1.0,
            thickness=1.0,
        )
        self.calc = UG27Calcs(self.params)

    def test_min_thk_circ_stress(self):
        # P*R / (S*E_long - 0.6*P)
        expected = 100 * 12.0 / (20000 * 1.0 - 0.6 * 100)
        assert self.calc.min_thk_circ_stress() == pytest.approx(expected)

    def test_min_thk_longitudinal_stress(self):
        # P*R / (2*S*E_long + 0.4*P)
        expected = 100 * 12.0 / (2 * 20000 * 1.0 + 0.4 * 100)
        assert self.calc.min_thk_longitudinal_stress() == pytest.approx(expected)

    def test_design_thickness_is_max_of_both(self):
        t_circ = self.calc.min_thk_circ_stress()
        t_long = self.calc.min_thk_longitudinal_stress()
        assert self.calc.design_thickness() == pytest.approx(max(t_circ, t_long))

    def test_max_pressure_circ_stress(self):
        # S*E_long*t / (R + 0.6*t)
        expected = 20000 * 1.0 * 1.0 / (12.0 + 0.6 * 1.0)
        assert self.calc.max_pressure_circ_stress() == pytest.approx(expected)

    def test_max_pressure_longitudinal_stress(self):
        # 2*S*E_circ*t / (R - 0.4*t)
        expected = 2 * 20000 * 1.0 * 1.0 / (12.0 - 0.4 * 1.0)
        assert self.calc.max_pressure_longitudinal_stress() == pytest.approx(expected)

    def test_max_pressure_is_min_of_both(self):
        p_circ = self.calc.max_pressure_circ_stress()
        p_long = self.calc.max_pressure_longitudinal_stress()
        assert self.calc.max_pressure() == pytest.approx(min(p_circ, p_long))

    def test_thin_wall_design_thickness_value(self):
        """UG-27 thin-wall result for 24-in ID, 100 psi, 20 ksi allowable."""
        # 100*12 / (20000 - 60) = 1200/19940 ≈ 0.06018 in
        assert self.calc.design_thickness() == pytest.approx(0.06018, abs=1e-4)

    def test_higher_pressure_requires_more_thickness(self):
        high_p_params = UG27params(
            inside_diameter=24.0,
            internal_pressure=500.0,
            allowable_stress=20000.0,
            joint_efficiency_long=1.0,
            joint_efficiency_circ=1.0,
            thickness=1.0,
        )
        high_p_calc = UG27Calcs(high_p_params)
        assert high_p_calc.design_thickness() > self.calc.design_thickness()

    def test_lower_joint_efficiency_reduces_max_pressure(self):
        low_e_params = UG27params(
            inside_diameter=24.0,
            internal_pressure=100.0,
            allowable_stress=20000.0,
            joint_efficiency_long=0.85,
            joint_efficiency_circ=0.85,
            thickness=1.0,
        )
        low_e_calc = UG27Calcs(low_e_params)
        assert low_e_calc.max_pressure() < self.calc.max_pressure()
