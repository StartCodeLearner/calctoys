import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from Cylinder.Calculations.Div2.Div2Cylinder_internal import (
    ShellType, t_min, sigma_theta_m, sigma_sm, tau,
    sigma_1, sigma_2, sigma_vm, compressive_stress_ok,
)

# Shared geometry for most tests
D_I = 20.0   # inner diameter
D_O = 24.0   # outer diameter
P = 100.0    # pressure
E = 1.0      # weld joint factor


class TestTMin:
    def test_value(self):
        # 0.5 * D_i * (exp(P / (S_ * E)) - 1)
        expected = 0.5 * 24.0 * (math.exp(100.0 / (20000.0 * 1.0)) - 1)
        assert t_min(100.0, 20000.0, 1.0, 24.0) == pytest.approx(expected)

    def test_higher_pressure_more_thickness(self):
        assert t_min(500.0, 20000.0, 1.0, 24.0) > t_min(100.0, 20000.0, 1.0, 24.0)

    def test_higher_allowable_stress_less_thickness(self):
        assert t_min(100.0, 30000.0, 1.0, 24.0) < t_min(100.0, 20000.0, 1.0, 24.0)


class TestSigmaThetaM:
    def test_cylinder(self):
        expected = P * D_I / (E * (D_O - D_I))
        assert sigma_theta_m(ShellType.CYLINDER, P, E, D_I, D_O) == pytest.approx(expected)

    def test_spherical(self):
        expected = P * D_I ** 2 / (E * (D_O ** 2 - D_I ** 2))
        assert sigma_theta_m(ShellType.SPHERICAL, P, E, D_I, D_O) == pytest.approx(expected)

    def test_conical(self):
        alpha = math.radians(10)
        expected = P * D_I / (E * (D_O - D_I) * math.cos(alpha))
        assert sigma_theta_m(ShellType.CONICAL, P, E, D_I, D_O, alpha=alpha) == pytest.approx(expected)

    def test_cylinder_stress_scales_linearly_with_pressure(self):
        s1 = sigma_theta_m(ShellType.CYLINDER, 100.0, E, D_I, D_O)
        s2 = sigma_theta_m(ShellType.CYLINDER, 200.0, E, D_I, D_O)
        assert s2 == pytest.approx(2 * s1)


class TestTau:
    def test_cylinder_zero_torque(self):
        result = tau(ShellType.CYLINDER, M=0, M_t=0, D_o=D_O, D=D_I, theta=0)
        assert result == pytest.approx(0.0)

    def test_cylinder_nonzero_torque(self):
        M_t = 1000.0
        expected = (16 * M_t * D_O) / (math.pi * (D_O ** 4 - D_I ** 4))
        assert tau(ShellType.CYLINDER, M=0, M_t=M_t, D_o=D_O, D=D_I, theta=0) == pytest.approx(expected)


class TestPrincipalStresses:
    """Pure pressure loading (M = F = M_t = 0) on a cylinder."""

    def _s_theta(self):
        return sigma_theta_m(ShellType.CYLINDER, P, E, D_I, D_O)

    def _s_m(self):
        return sigma_sm(ShellType.CYLINDER, M=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)

    def test_sigma_1_equals_max_stress_when_tau_zero(self):
        s1 = sigma_1(ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)
        assert s1 == pytest.approx(max(self._s_theta(), self._s_m()))

    def test_sigma_2_equals_min_stress_when_tau_zero(self):
        s2 = sigma_2(ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)
        assert s2 == pytest.approx(min(self._s_theta(), self._s_m()))

    def test_sigma_1_ge_sigma_2(self):
        s1 = sigma_1(ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)
        s2 = sigma_2(ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)
        assert s1 >= s2


class TestSigmaVmAndCheck:
    def test_von_mises_is_positive(self):
        result = sigma_vm(ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0)
        assert result > 0

    def test_compressive_stress_ok_below_allowable(self):
        # sigma_vm ≈ 433 for the test geometry; S=500 passes
        assert compressive_stress_ok(
            ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0, S=500.0
        )

    def test_compressive_stress_fails_below_stress(self):
        # sigma_vm ≈ 433 for the test geometry; S=400 fails
        assert not compressive_stress_ok(
            ShellType.CYLINDER, M=0, M_t=0, F=0, P=P, E=E, D=D_I, D_o=D_O, theta=0, S=400.0
        )
