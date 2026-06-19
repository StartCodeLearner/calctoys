"""ASME BPVC Section VIII, Division 1 -- Mandatory Appendix 13.

VESSELS OF NONCIRCULAR CROSS SECTION -- design facade.

The per-paragraph modules (`_Appendix13_7_a`, `_7_b`, `_7_c`, `_8_e`, `_9_b`,
`_6`) compute the membrane, bending and total stresses at the controlling
locations but stop short of the *design* decision (their source carries
"TODO: Implement acceptability tests"). This module adds that decision -- the
Appendix 13-4 stress-acceptance criteria -- and wraps the most common case
(unreinforced rectangular cross section, Fig. 13-2(a) sketch 1, 13-7(a)) in a
single easy call that returns a structured, checkable result.

Acceptance criteria (Appendix 13-4(b); US customary, psi):
  * membrane:            S_m            <= membrane_factor * S * E   (default 1.0)
  * membrane + bending:  |S_m + S_b|    <= bending_factor  * S * E   (default 1.5)
where S is the allowable stress and E the lower of the joint and ligament
efficiencies. The factors are exposed as parameters so a different Code edition
or a ligament-efficiency adjustment can be applied explicitly.

Units are US customary throughout: length in, pressure/stress psi.
"""
from dataclasses import dataclass, field

from ._Appendix13_7_a import Appendix13_7_aParams, Appendix13_7_aCalcs


@dataclass
class StressPoint:
    """Stress state at one controlling location and wall face."""
    label: str          # e.g. "Q_short" (short-side corner)
    description: str
    wall: str           # "inner" or "outer"
    membrane: float     # S_m (psi)
    bending: float      # S_b (psi)
    total: float        # S_T = S_m + S_b (psi)


@dataclass
class Appendix13Result:
    paragraph: str
    S: float
    E: float
    membrane_allowable: float
    total_allowable: float
    points: list = field(default_factory=list)

    # --- governing values ---
    @property
    def governing_membrane(self) -> StressPoint:
        return max(self.points, key=lambda p: abs(p.membrane))

    @property
    def governing_total(self) -> StressPoint:
        return max(self.points, key=lambda p: abs(p.total))

    @property
    def membrane_ok(self) -> bool:
        return abs(self.governing_membrane.membrane) <= self.membrane_allowable

    @property
    def total_ok(self) -> bool:
        return abs(self.governing_total.total) <= self.total_allowable

    @property
    def ok(self) -> bool:
        return self.membrane_ok and self.total_ok

    def margin(self) -> float:
        """Lowest remaining fraction of allowable (>=0 means acceptable)."""
        m = 1.0 - abs(self.governing_membrane.membrane) / self.membrane_allowable
        b = 1.0 - abs(self.governing_total.total) / self.total_allowable
        return min(m, b)

    def rows(self):
        """(label, description, wall, S_m, S_b, S_T) tuples for reporting."""
        return [(p.label, p.description, p.wall, p.membrane, p.bending, p.total)
                for p in self.points]


# Controlling locations for 13-7(a), and the calc method names that yield them.
_RECT_LOCATIONS = [
    ("N", "midspan, short side", "SmShort", "S_b_N", "S_T_N"),
    ("Q_short", "corner, short side", "SmShort", "S_b_Q_short", "S_T_Q_short"),
    ("M", "midspan, long side", "SmLong", "S_b_M", "S_T_M"),
    ("Q_long", "corner, long side", "SmLong", "S_b_Q_long", "S_T_Q_long"),
]


def design_rectangular_unreinforced(
        P, S, E,
        long_side_inside, short_side_inside,
        short_side_thickness, long_side_thickness,
        *, membrane_factor=1.0, bending_factor=1.5):
    """Design check for an unreinforced rectangular cross-section vessel under
    internal pressure (Appendix 13-7(a), Fig. 13-2(a) sketch 1).

    Evaluates every controlling location at both the inner and outer wall fibre
    and applies the 13-4(b) acceptance criteria. Returns an Appendix13Result.

    Args (US customary, in / psi):
        P  internal pressure
        S  allowable stress
        E  efficiency (lower of joint / ligament efficiency)
        long_side_inside, short_side_inside   inside lengths h, H
        short_side_thickness, long_side_thickness   t_1, t_2
    """
    points = []
    for wall, outer in (("inner", False), ("outer", True)):
        params = Appendix13_7_aParams(
            long_side_length_inside=long_side_inside,
            short_side_length_inside=short_side_inside,
            internal_pressure=P,
            short_side_thickness=short_side_thickness,
            long_side_thickness=long_side_thickness,
            allowable_stress=S,
            joint_efficiency=E,
            eval_at_outer_walls=outer,
        )
        calc = Appendix13_7_aCalcs(params)
        for label, desc, m_attr, b_attr, t_attr in _RECT_LOCATIONS:
            points.append(StressPoint(
                label=label, description=desc, wall=wall,
                membrane=getattr(calc, m_attr)(),
                bending=getattr(calc, b_attr)(),
                total=getattr(calc, t_attr)(),
            ))

    return Appendix13Result(
        paragraph="VIII-1 Appendix 13-7(a)",
        S=S, E=E,
        membrane_allowable=membrane_factor * S * E,
        total_allowable=bending_factor * S * E,
        points=points,
    )


if __name__ == "__main__":
    # Example from _Appendix13_7_a.py __main__.
    r = design_rectangular_unreinforced(
        P=400, S=20000, E=1.0,
        long_side_inside=9.5, short_side_inside=7.375,
        short_side_thickness=0.875, long_side_thickness=0.875,
    )
    print(f"{r.paragraph}: membrane allowable {r.membrane_allowable:.0f} psi, "
          f"total allowable {r.total_allowable:.0f} psi")
    gm, gt = r.governing_membrane, r.governing_total
    print(f"governing membrane: {gm.membrane:.1f} psi at {gm.label} ({gm.wall}) "
          f"-> {'OK' if r.membrane_ok else 'FAIL'}")
    print(f"governing total:    {gt.total:.1f} psi at {gt.label} ({gt.wall}) "
          f"-> {'OK' if r.total_ok else 'FAIL'}")
    print(f"overall: {'ACCEPTABLE' if r.ok else 'NOT ACCEPTABLE'} "
          f"(margin {r.margin() * 100:.1f}%)")
