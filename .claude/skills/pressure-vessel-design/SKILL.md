---
name: pressure-vessel-design
description: >
  Perform ASME BPVC Section VIII pressure-vessel design calculations using the
  calctoys Python modules in src/. Use when sizing or checking vessel
  components — cylindrical/spherical shells, heads, flanges, tubesheets,
  noncircular shells, saddle supports, or combined loading — under internal or
  external pressure per ASME VIII Div 1 (UG-27 etc.) or Div 2 (Part 4.3/4.4,
  Appendix 2/13/24, UHX). Also use to navigate this codebase's modules, their
  Code references, units, and the import quirks that make scripts "not work
  together."
---

# ASME Pressure Vessel Design (calctoys)

`src/` is a collection of Python implementations of ASME Boiler & Pressure
Vessel Code (BPVC) Section VIII calculations. It is a working engineer's
toolbox, not a polished library: modules are organized by component, mirror
the Code's variable names and equation numbers in comments, and — as the
README warns — **do not all import the same way, and some do not import at
all.** This skill is the map and the harness that make them usable.

## Golden rules

1. **Never hand-derive a Code formula you can call.** Find the module for the
   component + Code + Division, call it, report the labelled result. The
   modules encode equation numbers and edge cases you will otherwise get wrong.
2. **Bootstrap the path; do not guess imports.** Always start with
   `scripts/pv_env.py` `setup()` (or run scripts from `scripts/`). It puts both
   `src/` and `src/Tubesheet/UHX/` on `sys.path`, which is the only
   configuration where the working modules all import. See "Import quirks".
3. **Run the smoke test when unsure what works:** `python scripts/pv_env.py`
   prints a live OK/FAIL table. Trust that table over code comments.
4. **Units are US customary throughout** unless a module says otherwise:
   length **in**, pressure/stress **psi**, force **lbf**, moment **in·lbf**,
   angle **radians** (degrees only where a name says `_degrees`). Confirm the
   user's inputs are in these units before calling; convert if not.
5. **State the Code basis in every answer** — Section, Division, paragraph
   (e.g. "VIII-1 UG-27(c)(1)", "VIII-2 4.4.5"). The user is an engineer
   producing auditable calcs.

## Workflow

1. **Classify the problem:** component (shell / head / flange / tubesheet /
   noncircular / saddle / combined load), loading (internal vs external
   pressure, combined mechanical loads), and Code/Division. Ask the user only
   if it is genuinely ambiguous — most requests state it.
2. **Locate the module** using the map below, then open the relevant
   `references/*.md` for that family's exact entry points, parameter lists,
   and gotchas.
3. **Bootstrap and call.** `from pv_env import setup; setup()` then import and
   call. `scripts/example_cylinder.py` is the copy-me template for the call +
   labelled-output pattern.
4. **Report:** governing result with units, the Code paragraph, and any
   secondary values (e.g. both hoop and longitudinal thickness). Note any
   assumption you made (joint efficiency, material class, etc.).

## Module map (component → path → Code)

| Component / loading | Path under `src/` | Code basis |
|---|---|---|
| Cylinder, internal P, thin-wall | `Cylinder/Calculations/Div1/internal_pressure.py` | VIII-1 UG-27 |
| Cylinder/sphere/cone, internal P + combined | `Cylinder/Calculations/Div2/Div2Cylinder_internal.py` | VIII-2 4.3.3, 4.3.10 |
| Cylinder, external P + axial/bending/shear/combined | `Cylinder/Calculations/Div2/Div2Cylinder_external.py` | VIII-2 4.4.5 / 4.4.12 |
| Shared 4.4 buckling helpers (FS, F_ic) | `Cylinder/Calculations/Div2/Div2Part4_4_general.py` | VIII-2 4.4.2/4.4.3 |
| Tangent-modulus material model | `Cylinder/Calculations/Div2/Div2Annex3_D.py` | VIII-2 Annex 3-D |
| Hemispherical head, external P | `Cylinder/Calculations/Div2/Div2Hemispherical.py` | VIII-2 4.4.7 |
| Bolted flanges (integral/loose/optional) | `Flange/Traditional/Appendix_2.py`, `Flange/Calculations/` | VIII-1 App. 2 / VIII-2 4.16 |
| Clamp / metal-to-metal flanges | `Flange/Clamped/Appendix24.py`, `Flange/MetalToMetal/AppendixY.py` | VIII-1 App. 24 / App. Y |
| Bolt-load / gasket seating | `Flange/common/PCC_1.py`, `Div1Common.py` | App. 2 / PCC-1 |
| U-tube & fixed tubesheets | `Tubesheet/UHX/UHX_11.py`, `UHX_12.py`, `UHX_13.py` | VIII Part UHX |
| Tubesheet flanged extension | `Tubesheet/DIV2/FlangedExtension.py` | VIII-2 4.18 |
| TEMA tubesheet | `Tubesheet/TEMA/Calculations/RGP.py` | TEMA |
| Noncircular (rectangular) shells | `Noncircular/Calculations/_Appendix13_*.py` | VIII-1 App. 13 |
| Saddle supports (horizontal vessel) | `Saddles/Calculations/SaddleCalcsDiv2.py` | VIII-2 4.15 / Zick |
| Combined load aggregation (wind/platform) | `CombinedLoading/LoadingModel.py` | load model input to 4.3.10/4.4.12 |

For exact constructor signatures, method names, and per-family gotchas, read
the reference for the family you need:

- `references/cylinders-and-heads.md` — shells & heads, Div 1 and Div 2,
  internal/external/combined; the `material_type` enum.
- `references/flanges.md` — Appendix 2/24/Y; **circular-import gotcha**.
- `references/tubesheets.md` — UHX 11/12/13; **per-module import styles**.
- `references/noncircular-saddles-combined.md` — App. 13, saddles, load model.

## Import quirks (why scripts "don't work together")

`scripts/pv_env.py setup()` handles cases 1–2; case 3 (Flange) is now fixed.

1. **Package-relative modules** (Cylinder, Noncircular, Saddles,
   CombinedLoading, and `Tubesheet/UHX/UHX_12.py`): import as a dotted package
   path with `src/` on `sys.path`, e.g.
   `from Cylinder.Calculations.Div1 import internal_pressure`.
2. **Bare-import modules** (`Tubesheet/UHX/UHX_11.py`, `UHX_13.py`): use
   top-level imports like `from Table_13_1_and_2 import ...`, so they only
   resolve with `src/Tubesheet/UHX/` itself on `sys.path` and are imported by
   bare name: `import UHX_13`. **Do not mix** bare-imported UHX modules with
   the package-imported `UHX_12` in one session — `_UHX_common` then loads
   twice as two distinct modules and enum identity comparisons silently fail.
3. **Flange package now imports cleanly** (the old `Div1Common` ↔ `Appendix_2`
   circular import and several formula bugs were fixed). The App. 2 calc is
   still marked incomplete and is unvalidated against a known case — usable,
   but verify numbers. See `references/flanges.md`.

## Scripts

- `scripts/pv_env.py` — `setup()` path bootstrap + `python pv_env.py` smoke
  test (the ground-truth import table). Import it from any analysis script.
- `scripts/example_cylinder.py` — runnable worked example (Div 1 UG-27 +
  Div 2 4.3.3). The template for new calc scripts.
- `scripts/example_flange.py` — runnable App. 2 weld-neck flange example;
  doubles as the Flange-package regression check.
