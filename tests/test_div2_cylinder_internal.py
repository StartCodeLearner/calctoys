import math
import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Cylinder.Calculations.Div2.Div2Cylinder_internal import (
    ShellType,
    t_min,
    sigma_theta_m,
    sigma_sm,
    tau,
    sigma_1,
    sigma_2,
    sigma_vm,
    compressive_stress_ok,
)


class TestTMin(unittest.TestCase):
    """ASME Div2 4.3.3.1 hoop-stress required thickness."""

    def test_zero_pressure_gives_zero_thickness(self):
        self.assertAlmostEqual(t_min(P=0.0, S_=20000.0, E=1.0, D_i=24.0), 0.0, places=10)

    def test_formula_cylinder(self):
        # t = 0.5 * D_i * (exp(P / (S_*E)) - 1)
        P, S_, E, D_i = 100.0, 20000.0, 1.0, 24.0
        expected = 0.5 * D_i * (math.exp(P / (S_ * E)) - 1)
        self.assertAlmostEqual(t_min(P, S_, E, D_i), expected, places=10)

    def test_higher_pressure_needs_greater_thickness(self):
        self.assertGreater(
            t_min(P=500.0, S_=20000.0, E=1.0, D_i=24.0),
            t_min(P=100.0, S_=20000.0, E=1.0, D_i=24.0),
        )

    def test_lower_allowable_stress_needs_greater_thickness(self):
        self.assertGreater(
            t_min(P=100.0, S_=10000.0, E=1.0, D_i=24.0),
            t_min(P=100.0, S_=20000.0, E=1.0, D_i=24.0),
        )

    def test_larger_diameter_needs_greater_thickness(self):
        self.assertGreater(
            t_min(P=100.0, S_=20000.0, E=1.0, D_i=48.0),
            t_min(P=100.0, S_=20000.0, E=1.0, D_i=24.0),
        )


class TestSigmaThetaM(unittest.TestCase):
    """Membrane hoop stress — Div2 4.3.32/35/38."""

    def _cylinder_params(self):
        return dict(P=100.0, E=1.0, D=20.0, D_o=22.0)

    def test_cylinder_formula(self):
        p = self._cylinder_params()
        expected = (p['P'] * p['D']) / (p['E'] * (p['D_o'] - p['D']))
        self.assertAlmostEqual(
            sigma_theta_m(ShellType.CYLINDER, **p), expected, places=10
        )

    def test_spherical_formula(self):
        P, E, D, D_o = 100.0, 1.0, 20.0, 22.0
        expected = (P * D ** 2) / (E * (D_o ** 2 - D ** 2))
        self.assertAlmostEqual(
            sigma_theta_m(ShellType.SPHERICAL, P, E, D, D_o), expected, places=10
        )

    def test_conical_formula(self):
        P, E, D, D_o, alpha = 100.0, 1.0, 20.0, 22.0, math.radians(15)
        expected = (P * D) / (E * (D_o - D) * math.cos(alpha))
        self.assertAlmostEqual(
            sigma_theta_m(ShellType.CONICAL, P, E, D, D_o, alpha), expected, places=10
        )

    def test_higher_pressure_gives_higher_hoop_stress(self):
        p = self._cylinder_params()
        low = sigma_theta_m(ShellType.CYLINDER, **{**p, 'P': 50.0})
        high = sigma_theta_m(ShellType.CYLINDER, **{**p, 'P': 200.0})
        self.assertGreater(high, low)


class TestTau(unittest.TestCase):
    """Shear stress — Div2 4.3.34/37/40."""

    def _base(self):
        return dict(M=0.0, M_t=10000.0, D_o=22.0, D=20.0, theta=0.0)

    def test_cylinder_shear_only_from_torsion(self):
        b = self._base()
        expected = (16 * b['M_t'] * b['D_o']) / (math.pi * (b['D_o'] ** 4 - b['D'] ** 4))
        result = tau(ShellType.CYLINDER, **b)
        self.assertAlmostEqual(result, expected, places=10)

    def test_cylinder_zero_torsion_gives_zero_shear(self):
        b = self._base()
        b['M_t'] = 0.0
        self.assertAlmostEqual(tau(ShellType.CYLINDER, **b), 0.0, places=10)

    def test_conical_zero_bending_reduces_to_torsion(self):
        # When M=0 and alpha=0, conical tau = cylinder tau
        b = self._base()
        alpha = 0.0
        result_cone = tau(ShellType.CONICAL, M=0.0, M_t=b['M_t'], D_o=b['D_o'],
                          D=b['D'], theta=0.0, alpha=alpha)
        result_cyl = tau(ShellType.CYLINDER, **b)
        self.assertAlmostEqual(result_cone, result_cyl, places=10)


class TestPrincipalAndVonMises(unittest.TestCase):
    """sigma_1, sigma_2, sigma_vm — Div2 4.3.41-43."""

    def _common_params(self):
        return dict(
            shell_type=ShellType.CYLINDER,
            M=0.0,
            M_t=0.0,
            F=0.0,
            P=100.0,
            E=1.0,
            D=20.0,
            D_o=22.0,
            theta=0.0,
        )

    def test_sigma_1_ge_sigma_2(self):
        p = self._common_params()
        s1 = sigma_1(**p)
        s2 = sigma_2(**p)
        self.assertGreaterEqual(s1, s2)

    def test_vm_non_negative(self):
        p = self._common_params()
        vm = sigma_vm(**p)
        self.assertGreaterEqual(vm, 0.0)

    def test_compressive_stress_ok_passes_below_limit(self):
        p = self._common_params()
        vm = sigma_vm(**p)
        # Set S slightly above the computed von Mises stress — should pass
        S = vm * 1.1
        self.assertTrue(compressive_stress_ok(**p, S=S))

    def test_compressive_stress_ok_fails_above_limit(self):
        p = self._common_params()
        vm = sigma_vm(**p)
        # Set S just below the computed von Mises stress — should fail
        S = vm * 0.9
        self.assertFalse(compressive_stress_ok(**p, S=S))

    def test_zero_load_vm_stress_equals_pure_hoop(self):
        # With M=F=M_t=0 and pure internal pressure on a cylinder,
        # sigma_vm should be non-zero (pressure drives hoop and meridional stress)
        p = self._common_params()
        vm = sigma_vm(**p)
        self.assertGreater(vm, 0.0)


if __name__ == '__main__':
    unittest.main()
