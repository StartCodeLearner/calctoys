# calctoys

A collection of Python modules for pressure-vessel calculations per the
**ASME Boiler & Pressure Vessel Code (BPVC)**.

## Modules

| Module | ASME reference | Description |
|--------|---------------|-------------|
| `src/Cylinder/Cylinder.py` | — | High-level orchestrator; delegates to Div 1 and Div 2 calculators |
| `src/Cylinder/Calculations/Div1/internal_pressure.py` | UG-27 | Minimum wall thickness and MAWP for cylindrical shells under internal pressure (Div 1) |
| `src/Cylinder/Calculations/Div2/Div2Cylinder_internal.py` | Part 4.3 | Thick-wall hoop/meridional stress, Von Mises check for cylindrical, spherical, and conical shells (Div 2) |
| `src/Cylinder/Calculations/Div2/Div2Cylinder_external.py` | Part 4.4 | External-pressure buckling check (Div 2) |
| `src/Cylinder/Calculations/Div2/Div2Annex3_D.py` | Annex 3-D | Material curve look-up for external-pressure design |
| `src/Flange/Calculations/Appendix_2.py` | Appendix 2 | Traditional bolted-flange design (Div 1) |
| `src/Flange/Calculations/Div2Flange.py` | Part 4.16 | Bolted-flange design (Div 2) |
| `src/Flange/Clamped/` | Appendix 24 | Clamp-hub connector assembly |
| `src/Tubesheet/UHX/UHX_13.py` | UHX-13 | Fixed-tubesheet heat-exchanger calculations |
| `src/Tubesheet/UHX/UHX_11.py` | UHX-11 | Tubesheet attached to shell and channel |

## Quick start

### UG-27 — cylindrical shell under internal pressure (Div 1)

```python
from Cylinder.Cylinder import CylinderDesign

design = CylinderDesign(
    inside_diameter=24.0,        # inches
    internal_pressure=100.0,     # psi
    allowable_stress=20000.0,    # psi
    joint_efficiency_long=1.0,
    joint_efficiency_circ=1.0,
    thickness=0.5,               # inches (proposed wall)
)

print(design.report())
# {
#   'required_thickness': 0.0602,
#   'max_allowable_pressure': 1587.3,
#   'is_adequate': True,
#   ...
# }
```

### Running the GUI

```bash
cd src
python main.py
```

The GUI opens a UG-27 calculator panel: enter geometry and material properties,
then press **Calculate** to see the required thickness, MAWP, and pass/fail status.

## Running tests

```bash
pip install pytest
python -m pytest tests/
```

## Status

Most modules are functional for their primary use case. Some sub-modules
(e.g., `Saddles`, `Noncircular`) are stubs. Contributions and issue reports
are welcome — please open a GitHub issue to help prioritise work.
