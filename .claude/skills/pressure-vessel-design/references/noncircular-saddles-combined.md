# Reference: Noncircular Shells, Saddle Supports, Combined Loading

All paths relative to `src/`. Units: in / psi / lbf / in·lbf; angles radians
except fields named `_degrees`. Bootstrap: `from pv_env import setup; setup()`.

## VIII-1 Appendix 13 — noncircular (rectangular) vessels

`Noncircular/Calculations/`. **Note:** `Appendix13.py` is an empty
facade/aggregator (0 lines) — the actual rules live in the per-paragraph
private modules `_Appendix13_*.py`, with shared helpers in
`_Appendix13Common.py`.

Import the specific paragraph module you need, e.g.:

```python
from Noncircular.Calculations import _Appendix13_6   # multi-diameter hole, MultiDiameterHole
```

Paragraph modules present (map to App. 13 paragraphs/equations):
`_Appendix13_6`, `_7_a/_7_b/_7_c`, `_8_e/_8_f/_8_g/_8_h`,
`_9_b/_9_c/_9_d/_9_e`, `_10`, `_11`, `_12`, `_13`, plus `_Appendix13Common`.
Open the target file and follow its class/function names — they mirror the
App. 13 nomenclature and equation numbers in comments.

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
