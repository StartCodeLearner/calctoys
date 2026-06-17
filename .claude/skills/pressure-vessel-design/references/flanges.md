# Reference: Bolted & Clamped Flanges

All paths relative to `src/`. Units: in / psi / lbf / in·lbf.

## Import status — fixed; calc is usable but still incomplete

The Flange package used to fail on import (a circular dependency between
`Div1Common` and `Appendix_2`). **That is fixed** — all Flange modules now
import cleanly, and `scripts/example_flange.py` runs a full App. 2 weld-neck
flange end to end. The smoke test (`python scripts/pv_env.py`) lists them under
known-good.

Fixes applied (see git history for the commit):
- **Circular import**: `Div1Common` now imports `Appendix2FlangeCalcs` only
  under `TYPE_CHECKING` (it was used purely as a type annotation).
- **`Table_2_7_1.__init__`**: pulled `h_o` from the parent **flange** calc
  (`h_o = sqrt(B·g_o)`), not from `HubGeometry`, which has no `h_o` (was an
  `AttributeError` on every hub-stress calc).
- **`C_b`**: referenced a non-existent `Units.Metric`; now matches
  `Units.MKS`/`Units.SI` (the enum's actual members).
- **`B_1`**: `... or optional_flanges` (always truthy) corrected to
  `self.attachment_sketch in optional_flanges`.
- **`M_o_seating`**: lever arm `0.5*(C*G)` (dimensionally invalid) corrected to
  `0.5*(C-G)` = `W·h_G`.
- **`S_H` (operating & seating)**: operator-precedence bug — `f·M_o/L·g₁²·B`
  computed a value with the wrong dimensions; corrected to `f·M_o/(L·g₁²·B)`.
- **`Table_2_6.h_T`**: compared against non-existent `Table_2_5_2_Sketch.sketch_1`;
  corrected to the `Figure2_4` members actually used for `attachment_sketch`.

All of the above were applied to **both** copies (`Flange/Traditional/` and the
self-contained `Flange/Calculations/`).

### Still incomplete — verify before relying on numbers

`Appendix2FlangeCalcs` is marked `***Incomplete.***` in its docstring, with
open TODOs: **external pressure, reverse flanges, split flanges, allowable-
stress checks, noncircular bolt pattern, nut stops, material checks**. The
membrane/bending stress outputs (`S_H`, `S_R`, `S_T`) are now dimensionally
correct and in a sane range, but have **not** been validated against a known
ASME worked example. State this when you report results, and validate against a
reference case before trusting them for design.

## Module layout

| File | Scope | Code |
|---|---|---|
| `Flange/Traditional/Appendix_2.py` | Integral / loose / optional flange calc (`Appendix2FlangeCalcs`, `Appendix2Params`) | VIII-1 Appendix 2 |
| `Flange/Traditional/Div2Flange.py` | Div 2 flange variant | VIII-2 4.16 |
| `Flange/Calculations/Appendix_2.py`, `Div2Flange.py` | Parallel calc implementations | App. 2 / 4.16 |
| `Flange/common/Div1Common.py` | Shared tables & enums: `Table_2_7_1`, `Units`, `FacingType`, `Table_2_5_2_Sketch`, `Table_2_6`, `Figure_2_7_1`, flange-type sets | App. 2 tables |
| `Flange/common/PCC_1.py` | Bolt load / assembly (gasket seating) | ASME PCC-1 |
| `Flange/Clamped/Appendix24.py` | Clamp-connection flanges (`Appendix24Tests.py` alongside) | VIII-1 Appendix 24 |
| `Flange/MetalToMetal/AppendixY.py` | Metal-to-metal contact flanges | VIII-1 Appendix Y |

## `Appendix2Params` inputs (VIII-1 App. 2)

`Appendix2Params` collects the full flange definition. Key fields (all `None`
until set — populate every one you use):

- Pressure/material: `internal_pressure`, `flange_operating_allowable_stress`,
  `bolt_operating_allowable_stress`, `bolt_ambient_allowable_stress`,
  `nozzle_neck_operating_allowable`, `flange_operating_modulus_of_elasticity`,
  `flange_ambient_modulus_of_elasticity`.
- Gasket: `gasket_OD`, `gasket_ID`, `gasket_m`, `gasket_y`, `gasket_thickness`,
  `facing_sketch`, `facing_column`, `w`, `nubbin_height`, `raised_face_type`,
  `rf_dia`.
- Flange geometry: `flange_OD`, `flange_ID`, `flange_thickness`, `hub`,
  `attachment_sketch`.
- Bolting: `num_bolts`, `bolt_circle_diameter`, `bolt_dismeter` (sic — typo in
  source), `bolt_root_area`.
- Overrides: `custom_Wm1_active`/`custom_Wm1`, `custom_Wm2_active`/`custom_Wm2`,
  `custom_rigidity`; `units` (`Div1Common.Units`).

Method names in `Appendix2FlangeCalcs` mirror App. 2 variables; operating vs.
seating cases are distinguished by an `operating`/`bolting` suffix on the
method name (per the class docstring).

## Recommended approach for a flange request

1. Bootstrap and import normally (`from pv_env import setup; setup()`), then
   build params as in `scripts/example_flange.py`.
2. Report results with the App. 2 paragraph and units, and note that the calc
   is incomplete/unvalidated (above) — recommend checking against a known case.
3. If the user needs one of the missing features (external pressure, reverse/
   split flanges, allowable-stress checks, etc.), that's a code task: implement
   it on the designated branch **with a verified ASME test case**, since wrong
   flange math is a safety issue.
