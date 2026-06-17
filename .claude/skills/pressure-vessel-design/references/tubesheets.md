# Reference: Tubesheets (UHX / TEMA / Div 2)

All paths relative to `src/`. Units: in / psi / lbf / in·lbf.

## ⚠️ Import styles differ per UHX module — do not mix in one session

`scripts/pv_env.py setup()` puts **both** `src/` and `src/Tubesheet/UHX/` on
`sys.path` so all three import, but they use incompatible styles:

| Module | Import style in source | How to import |
|---|---|---|
| `UHX_11.py` | bare: `from _UHX_common import ...` | `import UHX_11` (top-level) |
| `UHX_13.py` | bare: `from Table_13_1_and_2 import ...`, `from _UHX_common import ...` | `import UHX_13` (top-level) |
| `UHX_12.py` | relative: `from ._UHX_common import ...` | `import Tubesheet.UHX.UHX_12` (package) |

**Hazard:** bare-importing `UHX_11`/`UHX_13` loads `_UHX_common` as top-level
module `_UHX_common`; package-importing `UHX_12` loads it again as
`Tubesheet.UHX._UHX_common`. The `Configuration`/`AttachmentType` enums then
exist as two unequal classes, so any `==` comparison or `isinstance` check that
crosses the boundary silently fails. **In one analysis, work entirely in one
style** — for a UHX-13 fixed-tubesheet calc use the bare-import world
(`UHX_11` + `UHX_13`), and don't also package-import `UHX_12`.

## VIII Part UHX — shell-and-tube tubesheets

The UHX rules build up: UHX-11 (general/effective elastic properties) feeds
UHX-12 (U-tube tubesheets) and UHX-13 (fixed tubesheets).

### UHX-11 — effective tubesheet properties (`UHX_11.py`)

`UHX11Params` → `UHX11`. Computes the perforated-plate effective properties:
`rho`, `D_o`, `mu`, `d_star`, `p_star`, `mu_star`, `hg_prime`, `E_star_ratio`,
`E_star`, `vu_star`, and `result()`. These outputs are the inputs the UHX-12 /
UHX-13 calcs expect (`D_o`, `mu`, `mu_star`, `h_prime_g`, `E_star`, `vu_star`).

### UHX-13 — fixed tubesheets (`UHX_13.py`)

`UHX_13_5_calcs(params)` is the main calc; `UHX_13_7` and `Bundle` are
supporting classes. `params` carries the UHX-11 tubesheet properties plus:
general (`config`, `is_operating_case`), design conditions (`P_s`, `P_t`
shell/tube-side pressures; `T_t_m`, `T_s_m`, `T_a` temperatures), and
allowables (`S`, `S_PS`, `W_star`, `E`, `E_star`, `h`, `A`, `C`).
`config` is a `_UHX_common.Configuration` enum value.

### UHX-12 — U-tube tubesheets (`UHX_12.py`)

`UHX_12_calcs(params)` with `params.UHX11`, `params.config`,
`params.tubesideAttachmentType` (a `_UHX_common.AttachmentType`). Uses
package-relative imports — import as `Tubesheet.UHX.UHX_12` (see hazard above).

### Supporting

- `_UHX_common.py` — `Configuration`, `AttachmentType`, `PitchType` enums and
  shared helpers.
- `Table_13_1_and_2.py` — `Table_13_1`, `Table_13_2` coefficient tables.
- `UHX_8.py` — UHX-8 rules.

## VIII-2 4.18 — flanged tubesheet extension

`Tubesheet/DIV2/FlangedExtension.py` (with `Tubesheet/DIV2/common.py`).

## TEMA

`Tubesheet/TEMA/Calculations/RGP.py` — TEMA RGP tubesheet rules (alternative to
ASME UHX; use when the user specifies TEMA).
