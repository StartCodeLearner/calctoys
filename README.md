# calctoys

A collection of Python scripts for pressure-vessel calculations per the ASME Boiler and Pressure Vessel Code (BPVC).

> **Note:** These scripts do not necessarily work together. If you find something useful or want to request a feature, please open an issue.

## Modules

### `src/Cylinder/Calculations/Div1/internal_pressure.py`

ASME BPVC Section VIII Division 1 — Paragraph UG-27 cylindrical shell under internal pressure.

| Class | Purpose |
|---|---|
| `UG27params` | Input data container (diameter, pressure, allowable stress, joint efficiencies, thickness) |
| `UG27Calcs` | Computes minimum required wall thickness and maximum allowable working pressure |

Key methods on `UG27Calcs`:
- `design_thickness()` — governing minimum thickness (greater of circumferential / longitudinal stress)
- `min_thk_circ_stress()` — UG-27(c)(1) circumferential stress formula
- `min_thk_longitudinal_stress()` — UG-27(c)(2) longitudinal stress formula
- `max_pressure()` — maximum allowable working pressure

### `src/Cylinder/Calculations/Div2/`

ASME BPVC Section VIII Division 2 — Part 4.3 shell thickness under internal / external pressure.

| File | Contents |
|---|---|
| `Div2Cylinder_internal.py` | Required thickness (4.3.3.1), membrane stresses, combined loads (4.3.10), von Mises stress check |
| `Div2Cylinder_external.py` | External-pressure buckling checks |
| `Div2Hemispherical.py` | Hemispherical head calculations |
| `Div2Part4_4_general.py` | Safety factors (4.4.2) and inelastic buckling stress `F_ic` |
| `Div2Annex3_D.py` | Annex 3-D material curve — tangent modulus `E_t` |
| `CalcExceptions.py` | `Div2CylinderException` |

## Running the tests

```bash
python -m pytest tests/
```

Or with the built-in `unittest` runner:

```bash
python -m unittest discover -s tests
```

## Running the UI

```bash
cd src
python main.py
```

Requires `tkinter` (included with most standard Python distributions).
