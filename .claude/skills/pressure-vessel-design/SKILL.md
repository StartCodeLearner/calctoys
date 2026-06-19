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

## Quick start

One command drives everything — no need to remember paths or import quirks
(`scripts/pv.py`, runnable from any directory):

```
python scripts/pv.py            # help
python scripts/pv.py check      # which modules import (smoke test)
python scripts/pv.py list       # list runnable worked examples
python scripts/pv.py run heads  # run one (cylinder | heads | flange | noncircular)
python scripts/pv.py test       # validation + regression suite
```

The `run <example>` files double as copy-me templates for the standard pattern:
`units` (convert/validate inputs) → call the calc module → `report` (audit
sheet). For a calc the examples don't cover, follow the Workflow below.

## Golden rules

1. **Never hand-derive a Code formula you can call.** Find the module for the
   component + Code + Division, call it, report the labelled result. The
   modules encode equation numbers and edge cases you will otherwise get wrong.
2. **Bootstrap the path; do not guess imports.** Always start with
   `scripts/pv_env.py` `setup()` (or run scripts from `scripts/`). It puts
   `src/` on `sys.path`; every module then imports by its dotted package path.
   See "Imports".
3. **Run the smoke test when unsure what works:** `python scripts/pv.py check`
   prints a live OK/FAIL table. Trust that table over code comments.
4. **Units are US customary throughout** unless a module says otherwise:
   length **in**, pressure/stress **psi**, force **lbf**, moment **in·lbf**,
   angle **radians** (degrees only where a name says `_degrees`). Convert and
   sanity-check inputs with `scripts/units.py` (`to_in`, `to_psi`, `to_lbf`,
   `to_in_lbf`, `deg2rad`, `sanity_check`) before calling — unit mismatch is
   the most likely source of a wrong answer.
5. **State the Code basis in every answer** — Section, Division, paragraph
   (e.g. "VIII-1 UG-27(c)(1)", "VIII-2 4.4.5"). The user is an engineer
   producing auditable calcs. Use `scripts/report.py` (`CalcReport`) to emit an
   inputs → intermediates → result → pass/fail → citation sheet.
6. **Distinguish validated from unvalidated.** Calcs covered by
   `scripts/tests.py` against hand-computed values (UG-27, UG-32 heads, VIII-2
   4.3.3) are trustworthy. Others (notably the App. 2 flange) are dimensionally
   correct but **not** validated against a published case — say so, and run
   `python scripts/tests.py` after any change to `src/`.

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
| Formed heads & cones, internal P (hemi/ellipsoidal/torispherical/conical) | `Cylinder/Calculations/Div1/UG32_heads.py` | VIII-1 UG-32 |
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
| Noncircular cross-section vessels (design check) | `Noncircular/Calculations/Appendix13.py` | VIII-1 App. 13-7(a) + 13-4 |
| Noncircular stress calcs (rectangular variants, ligaments) | `Noncircular/Calculations/_Appendix13_*.py` | VIII-1 App. 13 |
| Saddle supports (horizontal vessel) | `Saddles/Calculations/SaddleCalcsDiv2.py` | VIII-2 4.15 / Zick |
| Combined load aggregation (wind/platform) | `CombinedLoading/LoadingModel.py` | load model input to 4.3.10/4.4.12 |

For exact constructor signatures, method names, and per-family gotchas, read
the reference for the family you need:

- `references/cylinders-and-heads.md` — shells & heads, Div 1 and Div 2,
  internal/external/combined; UG-32 heads; the `material_type` enum.
- `references/flanges.md` — Appendix 2/24/Y; fixed bugs + remaining gaps.
- `references/tubesheets.md` — UHX 11/12/13, TEMA, Div 2 flanged extension.
- `references/noncircular-saddles-combined.md` — App. 13, saddles, load model.
- `references/module-index.generated.md` — full auto-generated map of every
  module's public symbols (regenerate with `scripts/index_modules.py --write`).

## Imports

`scripts/pv_env.py setup()` puts `src/` on `sys.path`; **every** calctoys
module then imports by its dotted package path, e.g.
`from Cylinder.Calculations.Div1 import internal_pressure` or
`import Tubesheet.UHX.UHX_13`. Run `python scripts/pv.py check` for the live
import table.

The repo's old "scripts don't work together" hazards are fixed: the Flange
circular import (`Div1Common` ↔ `Appendix_2`) and the UHX bare-vs-relative
import split are both resolved. (The App. 2 flange calc still imports but is
incomplete and unvalidated — see `references/flanges.md`.) If a module ever
fails to import, the smoke test reports it under known-broken rather than
silently breaking a calc.

## Scripts

Harness:
- `scripts/pv.py` — **one-command CLI** (`check` / `list` / `run` / `test` /
  `index`). The easiest way in; see Quick start above.
- `scripts/pv_env.py` — `setup()` path bootstrap + `python pv_env.py` smoke
  test (the ground-truth import table). Import it from any analysis script.
- `scripts/units.py` — unit conversion (`to_in`, `to_psi`, `to_lbf`,
  `to_in_lbf`, `deg2rad`) and `sanity_check(...)` magnitude guard.
- `scripts/report.py` — `CalcReport` builder → plain-text / Markdown calc sheet.
- `scripts/index_modules.py` — regenerate `references/module-index.generated.md`.
- `scripts/tests.py` — validation + regression suite. **Run after any `src/`
  change:** `python scripts/tests.py`.

Worked examples (copy-me templates, each runnable):
- `scripts/example_cylinder.py` — Div 1 UG-27 + Div 2 4.3.3 shells.
- `scripts/example_heads.py` — UG-32 head with the full units → calc → report
  pipeline.
- `scripts/example_flange.py` — App. 2 weld-neck flange; also the Flange
  regression check.
- `scripts/example_noncircular.py` — App. 13-7(a) rectangular vessel design
  check (stresses + 13-4 acceptance).

## Coverage & roadmap

Implemented and **validated** (tests.py): UG-27 cylinders, UG-32 formed
heads/cones (internal P), VIII-2 4.3.3 shells, App. 13-7(a) unreinforced
rectangular noncircular vessels (stresses + 13-4 acceptance). Present but
**unvalidated**: VIII-2 4.4 external/combined, App. 2 flange (incomplete),
UHX tubesheets, App. 13 stress modules beyond 13-7(a), saddles, combined-load
model — usable, verify numbers.

Known gaps (not yet implemented — say so rather than improvising): formed heads
under **external** pressure (UG-33), **nozzle/opening reinforcement**
(UG-37/UG-40, area-replacement), App. 13 design facade for the reinforced/
rounded-corner/obround cases (`_7_b`/`_7_c`/`_8_e`/`_9_b` — stresses exist,
wrap them with acceptance like `Appendix13.py` does for 13-7(a)), and the
App. 2 flange TODOs (external pressure, reverse/split flanges, allowable-stress
checks, nut stops, material checks). Implement these only with a verified ASME
test case added to `tests.py` — wrong vessel math is a safety issue.
