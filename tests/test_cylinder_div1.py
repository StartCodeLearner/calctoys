import math

import pytest

from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


def _calc(**overrides):
    kwargs = dict(
        inside_diameter=24.0,
        internal_pressure=100.0,
        allowable_stress=20000.0,
        joint_efficiency_long=1.0,
        joint_efficiency_circ=1.0,
        thickness=1.0,
    )
    kwargs.update(overrides)
    return UG27Calcs(UG27params(**kwargs))


def test_ug27_min_thk_circ_stress_matches_closed_form():
    P, S, E, R = 100.0, 20000.0, 1.0, 12.0
    expected = P * R / (S * E - 0.6 * P)
    assert _calc().min_thk_circ_stress() == pytest.approx(expected)


def test_ug27_min_thk_longitudinal_matches_closed_form():
    P, S, E, R = 100.0, 20000.0, 1.0, 12.0
    expected = P * R / (2 * S * E + 0.4 * P)
    assert _calc().min_thk_longitudinal_stress() == pytest.approx(expected)


def test_ug27_design_thickness_is_max_of_two():
    c = _calc()
    assert c.design_thickness() == max(
        c.min_thk_circ_stress(), c.min_thk_longitudinal_stress()
    )


def test_ug27_max_pressure_is_min_of_two():
    c = _calc()
    assert c.max_pressure() == min(
        c.max_pressure_circ_stress(), c.max_pressure_longitudinal_stress()
    )


def test_ug27_thicker_shell_holds_more_pressure():
    p_thin = _calc(thickness=0.5).max_pressure()
    p_thick = _calc(thickness=1.0).max_pressure()
    assert p_thick > p_thin


def test_ug27_design_thickness_scales_with_pressure():
    t_low = _calc(internal_pressure=100.0).design_thickness()
    t_high = _calc(internal_pressure=500.0).design_thickness()
    assert t_high > t_low
    assert math.isfinite(t_low) and math.isfinite(t_high)
