# Reference: Noncircular Shells, Saddle Supports, Combined Loading

All paths relative to `src/`. Units: in / psi / lbf / in·lbf; angles radians
except fields named `_degrees`. Bootstrap: `from pv_env import setup; setup()`.

## VIII-1 Appendix 13 — vessels of noncircular cross section

`Noncircular/Calculations/`.

### Design facade — `Appendix13.py` (start here)

`Appendix13.py` is the **design entry point**: it runs the stress calc *and*
applies the Appendix 13-4 acceptance criteria (the per-paragraph modules only
compute stresses — their source carries "TODO: Implement acceptability tests").
Validated by `scripts/tests.py`.

```python
from Noncircular.Calculations.Appendix13 import design_rectangular_unreinforced

r = design_rectangular_unreinforced(
    P=400, S=20000, E=1.0,            # pressure, allowable stress, efficiency
    long_side_inside=9.5, short_side_inside=7.375,
    short_side_thickness=0.875, long_side_thickness=0.875)

r.ok                  # overall acceptable?  (membrane_ok and total_ok)
r.governing_total     # StressPoint: label, wall, membrane, bending, total
r.governing_membrane
r.margin()            # lowest remaining fraction of allowable (>=0 = pass)
r.rows()              # full (label, desc, wall, S_m, S_b, S_T) table
```

Acceptance criteria (Appendix **13-4(b)**), US customary psi:
- membrane: `S_m <= membrane_factor·S·E` (default factor 1.0)
- membrane + bending: `|S_m + S_b| <= bending_factor·S·E` (default 1.5)

`S` is the allowable stress; `E` is the **lower** of the joint and ligament
efficiency (compute ligament efficiency from `_Appendix13_6.MultiDiameterHole`
when the wall is drilled, then pass the governing `E`). Both factors are
keyword-overridable for a different Code edition. The facade evaluates every
controlling location (`N` short-side midspan, `Q_short` short-side corner, `M`
long-side midspan, `Q_long` long-side corner) at **both** inner and outer wall
fibres and reports the governing one.

### Per-paragraph stress modules (lower level)

For geometries the facade doesn't yet wrap, import the paragraph module and use
its `*Calcs` class directly (stresses only — apply 13-4(b) yourself, as the
facade does):

| Module | Geometry / case | Key class |
|---|---|---|
| `_Appendix13_7_a` | unreinforced rectangular, Fig. 13-2(a) sk.1 | `Appendix13_7_aCalcs` |
| `_Appendix13_7_b` | rectangular, two long-side thicknesses | `Appendix13_7_bCalcs` |
| `_Appendix13_7_c` | rectangular with rounded corners | `Appendix13_7_cCalcs` |
| `_Appendix13_8_e` | reinforced/stayed rectangular | `_Appendix13_8_eCalcs` |
| `_Appendix13_9_b` | stayed rectangular (stay plate) | `Appendix13_9_bCalcs` |
| `_Appendix13_6` | ligament efficiency, multi-diameter holes | `MultiDiameterHole` |

Each `*Calcs` exposes `SmShort`/`SmLong` (membrane), `S_b_*` (bending) and
`S_T_*` (total) at the controlling locations, plus `eval_at_outer_walls` to
switch wall face. `_Appendix13Common.NonCircularVesselType` enumerates the
Fig. 13-2 sketches. Modules `_8_f/_8_g/_8_h`, `_9_c/_9_d/_9_e`, `_10`–`_13`
exist but are empty stubs. **Coverage gap:** only the unreinforced-rectangular
case is wrapped in the facade with a validated acceptance test; extending the
facade to `_7_b/_7_c/_8_e/_9_b` is straightforward future work (add each with a
verified case to `tests.py`).

## VIII-2 4.15 (Zick analysis) — saddle supports for horizontal vessels

`Saddles/Calculations/SaddleCalcsDiv2.py`

```python
from Saddles.Calculations.SaddleCalcsDiv2 import (
    SaddleParams, SaddleCalcsDiv2, SaddleRings, HeadType, Side,
)
```

`SaddleParams(...)` is a wide constructor — supply all of:
- Identity/side: `component_name`, `which_side` (`Side` enum),
  `is_exceptional_condition`.
- Loads/pressure: `internal_pressure`, `load` (load on **one** saddle, lbf),
  `contact_angle_degrees` (saddle wrap angle, **degrees**).
- Vessel geometry: `outside_radius` (in), `shell_thickness`, `head_thickness`,
  `head_inside_radius`, `head_depth`, `head_type` (`HeadType` enum),
  `vessel_tangent_length`, `tan_dist` (saddle-to-tangent distance).
- Material: `shell_modulus_of_elasticity`, `cylinder_allowable_stress`,
  `wear_plate_allowable`.
- Saddle: `saddle_width`, `web_thickness`, `base_plate_thickness`,
  `saddle_welded_to_vessel`.
- Wear plate: `wear_plate_present`, `wear_plate_welded_to_shell`,
  `wear_plate_thickness`, `wear_plate_width`, `wear_plate_angle`.
- Optional stiffening: `rings` (a `SaddleRings`, default `None`).

The constructor calls `isSane()` and raises `ValueError("Zero or None passed
into SaddleParams object")` if `outside_radius` is missing — populate every
field. `SaddleCalcsDiv2(params)` then exposes the Zick coefficients and
stresses as `calcK1..K10`, `calcSigma1..Sigma4` (longitudinal bending,
tangential shear, circumferential), `calcM1/M2`, `calcT`, etc., mirroring 4.15.

## Combined loading — load aggregation

`CombinedLoading/LoadingModel.py`. Builds the net force/moment set (e.g. wind,
platform, lateral loads) that feeds the combined-load checks in VIII-2 4.3.10 /
4.4.12.

```python
from CombinedLoading.LoadingModel import (
    LoadingModel, LateralLoad, VerticalLoad, PlatformLoad,
)

m = LoadingModel(
    support_length=...,
    support_attachment_elevation=...,
    vessel_tangent_distance_below_attachment_point=...,
)
m.add_load_source(some_load_source)   # anything exposing get_loads()
m.total_force_x(); m.total_force_y()
m.total_moment_x(); m.total_moment_y()
```

`Load` is an abstract base; `LateralLoad`, `VerticalLoad`, and `PlatformLoad`
are concrete sources. Feed the resulting `F`/`M`/`V` into the Div 2
external/combined functions in `references/cylinders-and-heads.md`.
