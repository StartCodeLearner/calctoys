"""Import bootstrap and smoke test for the calctoys ASME pressure-vessel modules.

The calctoys source tree mixes three incompatible import styles (see the
README's warning that "most of these scripts do not work together"):

  1. Package-relative imports under ``src`` (Cylinder, Noncircular, Saddles,
     CombinedLoading) -- work once ``src`` is on ``sys.path``.
  2. Bare top-level imports inside ``src/Tubesheet/UHX`` (e.g.
     ``from Table_13_1_and_2 import ...``) -- need the UHX directory itself on
     ``sys.path``.
  3. Circular imports in the Flange package (Div1Common <-> Appendix_2) that
     fail on import regardless of path.

``setup()`` puts (1) and (2) on the path so the working modules import the same
way every time, no matter the current working directory. Run this file directly
to print a status table of what imports cleanly -- that table is the ground
truth; trust it over comments in the code.

Usage:
    from pv_env import setup, SRC
    setup()
    from Cylinder.Calculations.Div1 import internal_pressure

    # or, as a smoke test:
    python pv_env.py
"""
from __future__ import annotations

import importlib
import os
import sys

# scripts/ -> pressure-vessel-design/ -> skills/ -> .claude/ -> repo root
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 4))
SRC = os.path.join(_REPO_ROOT, "src")
_UHX = os.path.join(SRC, "Tubesheet", "UHX")


def setup() -> str:
    """Put the calctoys source roots on sys.path. Idempotent. Returns SRC."""
    for path in (SRC, _UHX):
        if path not in sys.path:
            sys.path.insert(0, path)
    return SRC


# (module path, import name). Import names use the bare form for UHX modules.
_KNOWN_GOOD = [
    "Cylinder.Calculations.Div1.internal_pressure",
    "Cylinder.Calculations.Div2.Div2Cylinder_internal",
    "Cylinder.Calculations.Div2.Div2Cylinder_external",
    "Cylinder.Calculations.Div2.Div2Hemispherical",
    "Cylinder.Calculations.Div2.Div2Part4_4_general",
    "Cylinder.Calculations.Div2.Div2Annex3_D",
    "Noncircular.Calculations._Appendix13_6",
    "Saddles.Calculations.SaddleCalcsDiv2",
    "CombinedLoading.LoadingModel",
    "UHX_13",            # bare imports -> import as top-level module name
    "UHX_11",            # bare imports -> import as top-level module name
    "Tubesheet.UHX.UHX_12",  # relative imports -> import via package path
    # Flange package -- the Div1Common <-> Appendix_2 circular import is fixed.
    "Flange.common.Div1Common",
    "Flange.Traditional.Appendix_2",
    "Flange.Calculations.Appendix_2",
    "Flange.Clamped.Appendix24",
    "Flange.MetalToMetal.AppendixY",
]

# Modules known to fail on import (documented so failures are not surprising).
_KNOWN_BROKEN: list[str] = []


def _probe(name: str) -> tuple[bool, str]:
    try:
        importlib.import_module(name)
        return True, ""
    except Exception as exc:  # noqa: BLE001 - we want every failure reason
        return False, f"{type(exc).__name__}: {exc}"


def smoke_test() -> int:
    setup()
    print(f"SRC = {SRC}\n")
    failures = 0
    print("Known-good modules:")
    for name in _KNOWN_GOOD:
        ok, err = _probe(name)
        print(f"  [{'OK ' if ok else 'FAIL'}] {name}{'' if ok else '  -> ' + err}")
        if not ok:
            failures += 1

    print("\nKnown-broken modules (expected to fail):")
    if not _KNOWN_BROKEN:
        print("  (none)")
    for name in _KNOWN_BROKEN:
        ok, err = _probe(name)
        status = "still-broken" if not ok else "NOW-WORKS?!"
        print(f"  [{status}] {name}{'' if ok else '  -> ' + err}")

    print(f"\n{len(_KNOWN_GOOD) - failures}/{len(_KNOWN_GOOD)} known-good modules imported cleanly.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(smoke_test())
