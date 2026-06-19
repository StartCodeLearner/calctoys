"""Worked example: unreinforced rectangular (noncircular) vessel design.

ASME VIII-1 Appendix 13-7(a). Shows the full pipeline: units -> design facade
(stresses + 13-4 acceptance check) -> audit-ready report with the governing
location and pass/fail.

Run:  python example_noncircular.py
"""
from pv_env import setup

setup()

from units import sanity_check  # noqa: E402
from report import CalcReport  # noqa: E402
from Noncircular.Calculations.Appendix13 import (  # noqa: E402
    design_rectangular_unreinforced, design_rectangular_stayed)


def main() -> None:
    # Inputs (this example happens to already be US customary).
    P, S, E = 400.0, 20000.0, 1.0
    long_inside, short_inside = 9.5, 7.375
    t_short, t_long = 0.875, 0.875
    sanity_check(pressure_psi=P, stress_psi=S, length_in=long_inside)

    r = design_rectangular_unreinforced(
        P=P, S=S, E=E,
        long_side_inside=long_inside, short_side_inside=short_inside,
        short_side_thickness=t_short, long_side_thickness=t_long,
    )

    rpt = CalcReport("Unreinforced rectangular vessel", code=r.paragraph)
    rpt.input("P", P, "psi", "internal pressure")
    rpt.input("S", S, "psi", "allowable stress")
    rpt.input("E", E, "", "joint/ligament efficiency")
    rpt.input("h", long_inside, "in", "long side, inside")
    rpt.input("H", short_inside, "in", "short side, inside")
    rpt.input("t_1", t_short, "in", "short-side thickness")
    rpt.input("t_2", t_long, "in", "long-side thickness")

    # Show the governing stresses (full table is available via r.rows()).
    gm, gt = r.governing_membrane, r.governing_total
    rpt.intermediate("S_m,gov", gm.membrane, "psi",
                     f"{gm.label} ({gm.wall})")
    rpt.intermediate("S_T,gov", gt.total, "psi",
                     f"{gt.label} ({gt.wall})")
    rpt.result("membrane allowable (S*E)", r.membrane_allowable, "psi")
    rpt.result("total allowable (1.5*S*E)", r.total_allowable, "psi")
    rpt.result("margin", r.margin() * 100.0, "%", "lowest remaining margin")

    rpt.check("S_m <= S*E (13-4(b))", r.membrane_ok,
              f"{abs(gm.membrane):.0f} <= {r.membrane_allowable:.0f} psi")
    rpt.check("S_m+S_b <= 1.5*S*E (13-4(b))", r.total_ok,
              f"{abs(gt.total):.0f} <= {r.total_allowable:.0f} psi")
    rpt.note("Acceptance factors 1.0 / 1.5 per Appendix 13-4(b); pass E as the "
             "lower of joint and ligament efficiency.")
    print(rpt.render())

    # --- Stayed variant (13-9(b)): a stay plate adds a membrane-only check ---
    s = design_rectangular_stayed(
        P=100.0, S=20000.0, E=1.0,
        stay_pitch=5.0, short_side_inside=5.0,
        short_side_thickness=1.0, long_side_thickness=2.0,
        stay_plate_thickness=0.5)
    gm, gt = s.governing_membrane, s.governing_total
    print("\n" + "-" * 60)
    print(f"Stayed variant ({s.paragraph}): "
          f"governing membrane {gm.membrane:.0f} psi at {gm.label}, "
          f"governing total {gt.total:.0f} psi at {gt.label} -> "
          f"{'ACCEPTABLE' if s.ok else 'NOT ACCEPTABLE'} "
          f"(margin {s.margin() * 100:.1f}%)")


if __name__ == "__main__":
    main()
