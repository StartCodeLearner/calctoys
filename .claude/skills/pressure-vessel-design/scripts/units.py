"""Unit conversion + validation guard for calctoys.

The calctoys modules are unit-agnostic: they assume every input is already in
US customary (in / psi / lbf / in-lbf / radians) and never check. The most
likely way to get a confidently-wrong answer is to feed SI numbers into a US
customary formula. Use these helpers to convert inputs up front and to assert
that magnitudes look sane before calling a calc.

Examples:
    from units import to_in, to_psi, deg2rad, sanity_check
    D = to_in(1219.2, "mm")     # -> 48.0 in
    P = to_psi(2.76, "MPa")     # -> ~400 psi
    sanity_check(pressure_psi=P, length_in=D)   # warns if out of range
"""
from __future__ import annotations

import math
import warnings

# ---- Length -> inches ------------------------------------------------------
_LEN_TO_IN = {
    "in": 1.0, "inch": 1.0, "inches": 1.0,
    "ft": 12.0, "foot": 12.0, "feet": 12.0,
    "mm": 1.0 / 25.4,
    "cm": 1.0 / 2.54,
    "m": 1000.0 / 25.4,
}

# ---- Pressure / stress -> psi ----------------------------------------------
_PRESS_TO_PSI = {
    "psi": 1.0,
    "ksi": 1000.0,
    "pa": 1.0 / 6894.757293168, "Pa": 1.0 / 6894.757293168,
    "kpa": 1000.0 / 6894.757293168, "kPa": 1000.0 / 6894.757293168,
    "mpa": 1_000_000.0 / 6894.757293168, "MPa": 1_000_000.0 / 6894.757293168,
    "bar": 100_000.0 / 6894.757293168,
}

# ---- Force -> lbf ----------------------------------------------------------
_FORCE_TO_LBF = {
    "lbf": 1.0, "lb": 1.0, "lbs": 1.0,
    "n": 1.0 / 4.4482216153, "N": 1.0 / 4.4482216153,
    "kn": 1000.0 / 4.4482216153, "kN": 1000.0 / 4.4482216153,
    "kgf": 9.80665 / 4.4482216153,
}

# ---- Moment -> in-lbf ------------------------------------------------------
_MOMENT_TO_INLBF = {
    "in-lbf": 1.0, "inlbf": 1.0, "in_lbf": 1.0,
    "ft-lbf": 12.0, "ftlbf": 12.0,
    "n-m": 1.0 / 0.1129848290, "nm": 1.0 / 0.1129848290, "N-m": 1.0 / 0.1129848290,
    "kn-m": 1000.0 / 0.1129848290, "kN-m": 1000.0 / 0.1129848290,
}


def _convert(value: float, unit: str, table: dict, kind: str) -> float:
    key = unit.strip()
    if key not in table and key.lower() not in table:
        raise ValueError(
            f"Unknown {kind} unit {unit!r}. Known: {sorted(set(table))}")
    factor = table.get(key, table.get(key.lower()))
    return value * factor


def to_in(value: float, unit: str = "in") -> float:
    return _convert(value, unit, _LEN_TO_IN, "length")


def to_psi(value: float, unit: str = "psi") -> float:
    return _convert(value, unit, _PRESS_TO_PSI, "pressure/stress")


def to_lbf(value: float, unit: str = "lbf") -> float:
    return _convert(value, unit, _FORCE_TO_LBF, "force")


def to_in_lbf(value: float, unit: str = "in-lbf") -> float:
    return _convert(value, unit, _MOMENT_TO_INLBF, "moment")


def deg2rad(degrees: float) -> float:
    return math.radians(degrees)


# ---- Sanity ranges (US customary) for typical Section VIII vessels ---------
# Wide bounds; the point is to catch order-of-magnitude unit mistakes
# (e.g. an MPa value of 2.76 left unconverted, or mm passed as inches).
_RANGES = {
    "pressure_psi": (0.1, 100_000.0),
    "stress_psi": (1_000.0, 120_000.0),
    "length_in": (0.001, 2_000.0),
    "force_lbf": (0.0, 1.0e8),
    "moment_in_lbf": (0.0, 1.0e10),
}


def sanity_check(strict: bool = False, **quantities) -> list[str]:
    """Warn (or raise, if strict) when a named quantity is outside the typical
    US-customary range for that kind. Keyword names must match _RANGES, e.g.
    sanity_check(pressure_psi=400, stress_psi=20000, length_in=48).
    Returns the list of warning messages."""
    msgs: list[str] = []
    for name, val in quantities.items():
        if name not in _RANGES:
            raise ValueError(
                f"No sanity range for {name!r}. Known: {sorted(_RANGES)}")
        lo, hi = _RANGES[name]
        if val is None:
            continue
        if not (lo <= val <= hi):
            msgs.append(
                f"{name}={val:g} is outside the typical US-customary range "
                f"[{lo:g}, {hi:g}] -- check units?")
    if msgs:
        if strict:
            raise ValueError("; ".join(msgs))
        for m in msgs:
            warnings.warn(m, stacklevel=2)
    return msgs


if __name__ == "__main__":
    assert abs(to_in(1219.2, "mm") - 48.0) < 1e-9
    assert abs(to_psi(2.7579, "MPa") - 400.0) < 0.5
    assert abs(to_lbf(4.4482216153, "kN") - 1000.0) < 1e-6
    print("to_in(1219.2 mm) =", to_in(1219.2, "mm"))
    print("to_psi(2.76 MPa) =", to_psi(2.76, "MPa"))
    # This should emit a warning (a Pa value left unconverted reads as huge psi):
    msgs = sanity_check(pressure_psi=2_760_000)
    assert msgs, "expected a sanity warning"
    print("units self-test OK")
