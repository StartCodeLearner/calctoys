import importlib


def test_div1common_imports_without_circular_error():
    # Regression: Flange.common.Div1Common <-> Flange.Traditional.Appendix_2
    # formed a circular import at module load time.
    importlib.import_module("Flange.common.Div1Common")
    importlib.import_module("Flange.Traditional.Appendix_2")


def test_appendix24_clamped_assembly_runs():
    from Flange.Clamped.Appendix24 import (
        DesignCondition, Material, Bolting, Hub, Clamp, Gasket, HubAndClamp,
    )

    condition = DesignCondition(
        is_operating=True, temperature=200, ambient_temperature=75,
        pressure=3000, bolting_is_controlled=False, has_retainer=False,
    )
    bolt = Bolting(material=Material(1), diameter=1.75, root_area=1.98)
    hub = Hub(
        sketch=Hub.Sketch.c, material=Material(2),
        outside_diameter=(18 + (12.75 + 2.75) * 2), inner_diameter=18,
        hub_cross_section_corner_radius=0.25, small_end_thickness=12.75,
        length_of_small_end=15, taper_length=2.75, neck_length=15,
        neck_thickness_at_shoulder=12.75, shoulder_thickness=7.321,
        shoulder_height=2.75, transition_angle=10, shoulder_angle=10,
        friction_angle=5,
    )
    clamp = Clamp(
        sketch=Clamp.Sketch.a, material=Material(3), bolt_circle_radius=32.25,
        clamp_inside_diameter=43.75, clamp_width=28,
        effective_clamp_thickness=7.625, effective_clamp_gap=14,
        corner_radius=0.25, distance_from_bolt_circle_to_clamp_od=3.7,
        effective_lip_length=2.75, lug_height=15, lug_width=28,
    )
    gasket = Gasket(outer_diameter=20, inner_diameter=18, gasket_factor=0, seating_stress=0)
    assy = HubAndClamp(
        design_data=condition, bolting=bolt, gasket=gasket, hub=hub, clamp=clamp,
    )
    result = assy.get_result()
    assert isinstance(result, dict)
    assert result["N_bolts"] == 4
