"""Import bootstrap and smoke test for the calctoys ASME pressure-vessel modules.

All calctoys modules now use package-relative imports under ``src`` (Cylinder,
Noncircular, Saddles, CombinedLoading, Tubesheet/UHX, Flange). ``setup()`` puts
``src`` on ``sys.path`` so every module imports the same way, by its dotted
package path, no matter the current working directory.

(History: the UHX modules once used bare top-level imports and the Flange
package had a circular import; both are fixed, so the old per-module
special-casing is gone.) Run this file directly to print a status table of what
imports cleanly -- that table is the ground truth; trust it over code comments.

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


def setup() -> str:
    """Put the calctoys src root on sys.path. Idempotent. Returns SRC."""
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    return SRC


# (module path, import name). Import names use the bare form for UHX modules.
_KNOWN_GOOD = [
    "Cylinder.Calculations.Div1.internal_pressure",
    "Cylinder.Calculations.Div2.Div2Cylinder_internal",
    "Cylinder.Calculations.Div2.Div2Cylinder_external",
    "Cylinder.Calculations.Div2.Div2Hemispherical",
    "Cylinder.Calculations.Div2.Div2Part4_4_general",
    "Cylinder.Calculations.Div2.Div2Annex3_D",
    "Noncircular.Calculations.Appendix13",       # design facade (acceptance check)
    "Noncircular.Calculations._Appendix13_6",
    "Saddles.Calculations.SaddleCalcsDiv2",
    "CombinedLoading.LoadingModel",
    # UHX modules now use package-relative imports consistently -- import via
    # the dotted package path (no more bare-import special case).
    "Tubesheet.UHX.UHX_11",
    "Tubesheet.UHX.UHX_12",
    "Tubesheet.UHX.UHX_13",
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
