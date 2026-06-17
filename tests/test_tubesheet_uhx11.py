import pytest

from Tubesheet.UHX.UHX_11 import UHX11Params, UHX11
from Tubesheet.UHX._UHX_common import PitchType


def _calc(**overrides):
    kwargs = dict(
        radius_to_outermost_tube_hole_center=30.0,
        nominal_tube_OD=1.0,
        nominal_tube_wall_thickness=0.083,
        modulus_of_elasticity_of_tubes_at_tubesheet_design_temperature=26900000,
        modulus_of_elasticity_for_tubesheet_material_at_tubesheet_design_temperature=26900000,
        allowable_stress_of_tubes_at_tubesheet_design_temperature=13400,
        allowable_stress_for_tubesheet_material_at_tubesheet_design_temperature=19000,
        tube_pitch=1.25,
        area_of_untubed_lanes=99.0,
        tube_side_pass_partition_groove_depth=0,
        tubesheet_corrosion_tube_side=0.5,
        tubesheet_thickness=5,
        expanded_depth_of_tube_in_tubesheet=5,
        pitch_type=PitchType.SQUARE,
    )
    kwargs.update(overrides)
    return UHX11(UHX11Params(**kwargs))


def test_uhx11_imports_as_package():
    # Regression: UHX_11 used a bare `from _UHX_common import ...` that only
    # worked as a script; it must import as a package member.
    import importlib

    importlib.import_module("Tubesheet.UHX.UHX_11")
    importlib.import_module("Tubesheet.UHX.UHX_13")


def test_uhx11_d_o_matches_definition():
    # D_o = 2*r_o + d_t for the reference geometry.
    assert _calc().D_o() == pytest.approx(2 * 30.0 + 1.0)


def test_uhx11_ligament_efficiency_in_unit_interval():
    mu = _calc().mu()
    mu_star = _calc().mu_star()
    assert 0.0 < mu < 1.0
    assert 0.0 < mu_star < 1.0


def test_uhx11_effective_modulus_below_solid():
    c = _calc()
    # Perforation always reduces the effective modulus below the solid value.
    assert 0.0 < c.E_star_ratio() < 1.0
    assert c.E_star() == pytest.approx(c.E_star_ratio() * c.E)


def test_uhx11_result_property_is_dict_with_expected_keys():
    result = _calc().result
    assert isinstance(result, dict)
    assert {"rho", "D_o", "mu", "E_star", "vu_star"} <= set(result)
