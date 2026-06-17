import math

import pytest

from Cylinder.Calculations.Div2 import (
    Div2Cylinder_internal as DC,
    Div2Hemispherical as DH,
    Div2Part4_4_general as DG,
)
from Cylinder.Calculations.Div2.Div2Annex3_D import Table3_D_1_Material


# --- 4.3.3.1 t_min ---------------------------------------------------------


def test_t_min_matches_closed_form():
    P, S, E, D_i = 100.0, 20000.0, 1.0, 24.0
    assert DC.t_min(P, S, E, D_i) == pytest.approx(0.5 * D_i * (math.exp(P / (S * E)) - 1))


def test_t_min_increases_with_pressure():
    a = DC.t_min(100.0, 20000.0, 1.0, 24.0)
    b = DC.t_min(500.0, 20000.0, 1.0, 24.0)
    assert b > a > 0


# --- 4.3.10 hoop stress ----------------------------------------------------


def test_sigma_theta_m_cylinder_matches_formula():
    P, E, D, D_o = 100.0, 1.0, 24.0, 26.0
    expected = (P * D) / (E * (D_o - D))
    assert DC.sigma_theta_m(DC.ShellType.CYLINDER, P, E, D, D_o) == pytest.approx(expected)


def test_sigma_theta_m_spherical_matches_formula():
    P, E, D, D_o = 100.0, 1.0, 24.0, 26.0
    expected = (P * D ** 2) / (E * (D_o ** 2 - D ** 2))
    assert DC.sigma_theta_m(DC.ShellType.SPHERICAL, P, E, D, D_o) == pytest.approx(expected)


def test_sigma_theta_m_conical_uses_cos_alpha():
    P, E, D, D_o, alpha = 100.0, 1.0, 24.0, 26.0, math.radians(15)
    cyl = DC.sigma_theta_m(DC.ShellType.CYLINDER, P, E, D, D_o)
    cone = DC.sigma_theta_m(DC.ShellType.CONICAL, P, E, D, D_o, alpha=alpha)
    assert cone == pytest.approx(cyl / math.cos(alpha))


# --- 4.4.7.1 hemispherical -------------------------------------------------


def test_F_he_matches_formula():
    assert DH.F_he(30e6, 0.5, 60.0) == pytest.approx(0.075 * 30e6 * (0.5 / 60.0))


def test_hemi_P_a_positive_and_consistent():
    P_a = DH.P_a(
        E_y=29e6, R_o=60.0, t=0.5,
        sigma_ys=30000.0, sigma_uts=60000.0,
        material_type=Table3_D_1_Material.FERRITIC_STEEL,
    )
    F_ha = DH.F_ha(
        29e6, 60.0, 0.5, 30000.0, 60000.0, Table3_D_1_Material.FERRITIC_STEEL,
    )
    assert P_a == pytest.approx(2 * F_ha * (0.5 / 60.0))
    assert P_a > 0


# --- 4.4.2 safety factor ---------------------------------------------------


@pytest.mark.parametrize(
    "F_ic,S_y,expected",
    [
        (10000.0, 30000.0, 2.0),
        (30000.0, 30000.0, 1.667),
        (45000.0, 30000.0, 0.0),
    ],
)
def test_FS_branches(F_ic, S_y, expected):
    assert DG.FS(F_ic, S_y) == pytest.approx(expected)


def test_FS_transition_zone_decreases_toward_yield():
    # In the 0.55*Sy < F_ic < Sy band, FS should drop from 2 toward ~1.69 as
    # F_ic approaches S_y.
    S_y = 30000.0
    low = DG.FS(0.6 * S_y, S_y)
    high = DG.FS(0.95 * S_y, S_y)
    assert low > high
    assert 1.5 < high < 2.0
