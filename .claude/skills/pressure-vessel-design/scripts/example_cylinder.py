"""Worked example: shell-thickness checks for a cylindrical shell.

Demonstrates the canonical workflow this skill follows:
  1. bootstrap sys.path via pv_env.setup()
  2. import the calc module for the right Code / Division
  3. build its params, call the public method, print labelled results with units

Run:  python example_cylinder.py

All quantities are US customary: lengths in inches, pressure/stress in psi,
forces in lbf, moments in in-lbf, angles in radians.
"""
from pv_env import setup

setup()

from Cylinder.Calculations.Div1 import internal_pressure as div1  # noqa: E402
from Cylinder.Calculations.Div2 import Div2Cylinder_internal as div2  # noqa: E402


def div1_ug27_example() -> None:
    """ASME VIII-1 UG-27: internal-pressure cylinder, thin-wall."""
    params = div1.UG27params(
        inside_diameter=24.0,       # in
        internal_pressure=100.0,    # psi
        allowable_stress=20000.0,   # psi (S)
        joint_efficiency_long=1.0,  # E for longitudinal seam (hoop stress)
        joint_efficiency_circ=1.0,  # E for circumferential seam (long. stress)
        thickness=1.0,              # in (used for MAWP checks)
    )
    calc = div1.UG27Calcs(params)
    print("ASME VIII-1 UG-27 (internal pressure cylinder)")
    print(f"  required thickness (governing) : {calc.design_thickness():.4f} in")
    print(f"    - hoop (circ. stress)        : {calc.min_thk_circ_stress():.4f} in")
    print(f"    - longitudinal stress        : {calc.min_thk_longitudinal_stress():.4f} in")
    print(f"  MAWP at t = {params.thickness} in (governing) : {calc.max_pressure():.1f} psi")


def div2_433_example() -> None:
    """ASME VIII-2 4.3.3: internal-pressure cylinder, exact (log) form."""
    t = div2.t_min(P=300.0, S_=20000.0, E=1.0, D_i=48.0)
    print("\nASME VIII-2 4.3.3.1 (internal pressure cylinder)")
    print(f"  required thickness : {t:.4f} in")


if __name__ == "__main__":
    div1_ug27_example()
    div2_433_example()
