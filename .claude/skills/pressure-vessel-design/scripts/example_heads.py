"""Worked example: UG-32 head thickness with the full skill pipeline.

Shows the recommended pattern end to end:
  units  -> convert/validate inputs (SI in, US customary out)
  calc   -> call the validated UG-32 module
  report -> emit an audit-ready calc sheet with a pass/fail check

Run:  python example_heads.py
"""
from pv_env import setup

setup()

from units import to_in, to_psi, sanity_check  # noqa: E402
from report import CalcReport  # noqa: E402
from Cylinder.Calculations.Div1 import UG32_heads as heads  # noqa: E402


def main() -> None:
    # Inputs arrive in SI; convert once, up front.
    D = to_in(1219.2, "mm")     # 48 in inside diameter
    P = to_psi(2.7579, "MPa")   # ~400 psi design pressure
    S = to_psi(120.66, "MPa")   # ~17500 psi allowable
    E = 1.0
    t_provided = to_in(15.875, "mm")   # 0.625 in nominal
    sanity_check(pressure_psi=P, stress_psi=S, length_in=D)

    # 2:1 ellipsoidal head (h = D/4 -> K = 1).
    t_req = heads.required_thickness(heads.HeadType.ELLIPSOIDAL, P, S, E, D=D, h=D / 4)
    P_mawp = heads.P_ellipsoidal(S, E, t_provided, D, h=D / 4)

    r = (CalcReport("2:1 ellipsoidal head thickness",
                    code="ASME VIII-1 UG-32(c)")
         .input("P", P, "psi", "design pressure (2.7579 MPa)")
         .input("S", S, "psi", "allowable stress (120.66 MPa)")
         .input("E", E, "", "joint efficiency")
         .input("D", D, "in", "inside diameter (1219.2 mm)")
         .intermediate("K", heads.K_ellipsoidal(D, D / 4), "", "shape factor (2:1)")
         .result("t_required", t_req, "in", "minimum required thickness")
         .result("MAWP", P_mawp, "psi", f"at t_provided = {t_provided:.3f} in")
         .check("t_provided >= t_required", t_provided >= t_req,
                f"{t_provided:.3f} >= {t_req:.3f} in")
         .note("UG-32 excludes corrosion allowance; add separately."))
    print(r.render())


if __name__ == "__main__":
    main()
