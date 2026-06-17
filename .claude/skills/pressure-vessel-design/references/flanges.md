# Reference: Bolted & Clamped Flanges

All paths relative to `src/`. Units: in / psi / lbf / in·lbf.

## ⚠️ Import gotcha — the Flange package is broken on import

`Flange.Traditional.Appendix_2` and `Flange.common.Div1Common` have a
**circular import**: `Div1Common` imports `Appendix2FlangeCalcs` from
`Appendix_2`, while `Appendix_2` imports a long list of names from
`Div1Common`. Importing either first triggers
`ImportError: ... partially initialized module`. `scripts/pv_env.py` lists both
under "known-broken" and the smoke test confirms they still fail.

Consequences and options:
- You **cannot** `import` these modules as-is to run a full flange calc.
- The formulas and tables are still valuable as a **reference**: read the file
  and copy the specific function/table you need into a standalone script, or
  break the cycle locally (e.g. move the `Appendix2FlangeCalcs` import in
  `Div1Common` to a deferred/in-function import) **only if the user asks you to
  fix it** — that is a code change, not a calc.
- `Flange/Traditional/Appendix_2.py` itself notes the class is **incomplete**
  (`***Incomplete.***`; TODOs for external pressure, reverse/split flanges,
  allowable stresses). Treat results as partial and say so.

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

1. Tell the user up front that the Flange modules don't import cleanly and the
   App. 2 class is marked incomplete.
2. If they want numbers now: read the relevant function from the file and run a
   copied, self-contained version, citing the exact App. 2 paragraph.
3. If they want the package fixed: that's a code task — break the circular
   import and complete TODOs on the designated branch, with tests.
