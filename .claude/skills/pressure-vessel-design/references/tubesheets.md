# Reference: Tubesheets (UHX / TEMA / Div 2)

All paths relative to `src/`. Units: in / psi / lbf / in·lbf.

## Imports — consistent package-relative style

All UHX modules now use package-relative imports, so they import the same way
as the rest of `src/` — by dotted package path, with `scripts/pv_env.py
setup()` on the path:

```python
from pv_env import setup; setup()
import Tubesheet.UHX.UHX_11 as uhx11
import Tubesheet.UHX.UHX_12 as uhx12
import Tubesheet.UHX.UHX_13 as uhx13
```

(Historical note: UHX_11/UHX_13 once used bare top-level imports while UHX_12
used relative ones, which loaded `_UHX_common` twice and made the
`Configuration`/`AttachmentType` enums compare unequal across modules. That is
fixed — import all three by package path and the shared enums are identical.)

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
