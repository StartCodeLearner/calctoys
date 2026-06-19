"""Worked example: ASME VIII-1 Appendix 2 integral weld-neck flange.

Exercises the Flange package end to end. Until the circular-import and formula
fixes, this module could not even be imported; this script doubles as a
regression check that it now both imports and produces dimensionally sane
results (bolt loads in lbf, moments in in-lbf, stresses in psi).

The Appendix 2 flange calc is still INCOMPLETE per the class docstring
(no external pressure, reverse/split flanges, allowable-stress checks, etc.).
Treat the stress outputs as indicative and verify against a known case before
relying on them. See references/flanges.md.

Run:  python example_flange.py
"""
from pv_env import setup

setup()

from Flange.Traditional.Appendix_2 import (  # noqa: E402
    Appendix2Params, Appendix2FlangeCalcs, HubGeometry,
)
from Flange.common.Div1Common import (  # noqa: E402
    Units, FacingType, Table_2_5_2_Sketch, Figure2_4,
)


def build_flange() -> Appendix2FlangeCalcs:
    p = Appendix2Params(None)
    # Design conditions
    p.internal_pressure = 400.0                  # psi
    p.bolt_ambient_allowable_stress = 25000.0    # psi (S_a)
    p.bolt_operating_allowable_stress = 25000.0  # psi (S_b)
    p.flange_operating_allowable_stress = 17500.0
    p.nozzle_neck_operating_allowable = 17500.0
    p.flange_operating_modulus_of_elasticity = 2.7e7
    p.flange_ambient_modulus_of_elasticity = 2.9e7
    p.custom_Wm1_active = False
    p.custom_Wm2_active = False
    # Gasket (spiral-wound, m/y typical)
    p.gasket_OD = 23.0
    p.gasket_ID = 21.0
    p.gasket_m = 3.75
    p.gasket_y = 7600.0
    p.gasket_thickness = 0.125
    p.facing_sketch = Table_2_5_2_Sketch.s_1a
    p.facing_column = 2
    p.w = 0.4
    p.raised_face_type = FacingType.raised_face
    p.rf_dia = 23.0
    # Flange geometry
    p.flange_OD = 27.0
    p.flange_ID = 19.25
    p.flange_thickness = 2.69
    p.num_bolts = 20
    p.bolt_circle_diameter = 25.0
    p.bolt_dismeter = 0.875        # (sic: source attribute name)
    p.bolt_root_area = 0.4418
    p.attachment_sketch = Figure2_4.sketch_2   # integral weld-neck
    p.custom_rigidity = None
    p.units = Units.Imperial
    p.hub = HubGeometry(None, smallendthickness=0.5, largeendthickness=1.0, length=2.0)
    return Appendix2FlangeCalcs(p)


def main() -> None:
    f = build_flange()
    print("ASME VIII-1 Appendix 2 integral weld-neck flange")
    print(f"  b   effective gasket width     : {f.b:.4f} in")
    print(f"  G   gasket reaction diameter   : {f.G:.4f} in")
    print(f"  W_m1 operating bolt load       : {f.W_m_1:.1f} lbf")
    print(f"  W_m2 seating bolt load         : {f.W_m_2:.1f} lbf")
    print(f"  A_m  required bolt area        : {f.A_m:.4f} in^2")
    print(f"  A_b  actual bolt area          : {f.A_b:.4f} in^2")
    print(f"  M_o  operating moment          : {f.M_o_operating:.1f} in-lbf")
    print(f"  M_o  seating moment            : {f.M_o_seating:.1f} in-lbf")
    print(f"  S_H  longitudinal hub stress   : {f.S_H_operating:.1f} psi")
    print(f"  S_R  radial flange stress      : {f.S_R_operating:.1f} psi")
    print(f"  S_T  tangential flange stress  : {f.S_T_operating:.1f} psi")


if __name__ == "__main__":
    main()
