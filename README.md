# calctoys

A collection of Python scripts for pressure-vessel calculations per the ASME Boiler & Pressure Vessel Code (BPVC).

## Modules

| Module | Status | Description |
|---|---|---|
| `src/Cylinder` | Active | Cylindrical shell thickness / MAWP calculations |
| `src/Flange` | Active | Flange design (Appendix 2, Div 2, clamped) |
| `src/Saddles` | Active | Horizontal vessel saddle support (Div 2) |
| `src/CombinedLoading` | Stub | Combined loading checks (not yet implemented) |
| `src/Noncircular` | Stub | Non-circular cross-section shells (not yet implemented) |
| `src/Tubesheet` | Stub | Tubesheet design (not yet implemented) |

## Cylinder module

### Div 1 — UG-27 (internal pressure)
`src/Cylinder/Calculations/Div1/internal_pressure.py`

```python
from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs

params = UG27params(
    inside_diameter=24.0,
    internal_pressure=100.0,
    allowable_stress=20000.0,
    joint_efficiency_long=1.0,
    joint_efficiency_circ=1.0,
    thickness=1.0,
)
cyl = UG27Calcs(params)
print(cyl.design_thickness())   # minimum required thickness
print(cyl.max_pressure())       # MAWP
```

### Div 2 — Part 4.3 / Annex 3-D (internal & external pressure)
`src/Cylinder/Calculations/Div2/`

## Running the tests

```bash
python -m pytest tests/
```

## Notes

Most scripts are standalone and do not share a common data layer. Contributions and issues are welcome!
