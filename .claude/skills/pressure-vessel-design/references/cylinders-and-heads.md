# Reference: Cylinders & Heads

All paths relative to `src/`. Units: in / psi / lbf / in·lbf / radians.
Bootstrap first: `from pv_env import setup; setup()`.

## VIII-1 UG-27 — cylinder, internal pressure (thin-wall)

`Cylinder/Calculations/Div1/internal_pressure.py`

```python
from Cylinder.Calculations.Div1 import internal_pressure as div1

p = div1.UG27params(
    inside_diameter=24.0,       # in
    internal_pressure=100.0,    # psi (P)
    allowable_stress=20000.0,   # psi (S)
    joint_efficiency_long=1.0,  # E, longitudinal seam -> governs hoop (circ.) stress
    joint_efficiency_circ=1.0,  # E, circumferential seam -> governs longitudinal stress
    thickness=1.0,              # in, only used by the max_pressure (MAWP) methods
)
c = div1.UG27Calcs(p)
c.design_thickness()             # max(hoop, longitudinal) required t  [in]
c.min_thk_circ_stress()          # hoop:  P R / (S E - 0.6 P)
c.min_thk_longitudinal_stress()  # long.: P R / (2 S E + 0.4 P)
c.max_pressure()                 # MAWP at given t = min(circ, long)
```

Note the param naming: `joint_efficiency_long` is applied to the hoop/circ.
stress thickness, `joint_efficiency_circ` to the longitudinal — matching how
`UG27Calcs` wires `E_long`/`E_circ`. Thin-wall form; for `t > R/2` or
`P > 0.385 S E`, UG-27 requires the thick-wall appendix (not implemented here).

## VIII-1 UG-32 — formed heads & cones, internal pressure

`Cylinder/Calculations/Div1/UG32_heads.py` (added to close a coverage gap;
free functions, **validated** by `scripts/tests.py` against hand-computed
closed-form values). US customary; thickness excludes corrosion allowance.

```python
from Cylinder.Calculations.Div1 import UG32_heads as heads

# Dispatch by head type (pass only the geometry that type needs):
heads.required_thickness(heads.HeadType.ELLIPSOIDAL, P=400, S=17500, E=1.0, D=48, h=12)
heads.required_thickness(heads.HeadType.HEMISPHERICAL, P=400, S=17500, E=1.0, L=24)
heads.required_thickness(heads.HeadType.TORISPHERICAL, P=400, S=17500, E=1.0, L=48, r=2.88)
heads.required_thickness(heads.HeadType.CONICAL, P=400, S=17500, E=1.0, D=48, alpha=0.349)
```

- Required thickness: `t_hemispherical(P,S,E,L)` (UG-32(f)),
  `t_ellipsoidal(P,S,E,D,h=,K=)` (UG-32(c)), `t_torispherical(P,S,E,L,r=,M=)`
  (UG-32(d)), `t_conical(P,S,E,D,alpha)` (UG-32(g)).
- MAWP at a given `t`: `P_hemispherical`, `P_ellipsoidal`, `P_torispherical`,
  `P_conical` (same args with `t` instead of `P`).
- Shape factors: `K_ellipsoidal(D,h)` = (1/6)[2+(D/2h)²] (=1 for a 2:1 head);
  `M_torispherical(L,r)` = ¼[3+√(L/r)] (≈1.77 for standard F&D, L=D, r=0.06D).
  Pass `K=`/`M=` directly to override, or `h=`/`r=` to compute them.
- `t_conical` raises `ValueError` for a half-apex angle ≥ 30° (UG-32(g) limit;
  use Appendix 1-5 toriconical/reinforcement above that).

For external-pressure heads see the Div 2 hemispherical module below; formed
heads under external pressure (UG-33) are a remaining gap (see SKILL.md).

## VIII-2 4.3 — cylinder/sphere/cone, internal pressure & combined

`Cylinder/Calculations/Div2/Div2Cylinder_internal.py` (module of free functions)

- `t_min(P, S_, E, D_i)` → required thickness, exact log form
  `0.5 D_i (exp(P/(S E)) - 1)` (4.3.3.1). `S_` is allowable stress, `E` joint
  efficiency, `D_i` inside diameter.
- Combined-load membrane stresses, 4.3.10 — selected by `ShellType` enum
  (`CYLINDER`, `SPHERICAL`, `CONICAL`):
  - `sigma_theta_m(shell_type, P, E, D, D_o, alpha=0)` — circ. membrane (4.3.32/35/38)
  - `sigma_sm(shell_type, M, F, P, E, D, D_o, theta, phi=0, alpha=0)` — meridional (4.3.33/36/39)
  - `tau(shell_type, M, M_t, D_o, D, theta, phi=0, alpha=0)` — shear (4.3.34/37/40)
  - `sigma_1` / `sigma_2` / `sigma_3` — principal stresses (4.3.41–43)
  - `sigma_vm(...)` — von Mises equivalent
  - `compressive_stress_ok(..., S, ...)` → bool, `sigma_vm <= S`

  Here `D` is the relevant diameter and `D_o` the outside diameter; `alpha` is
  the cone half-angle, `phi` the spherical meridional angle, `theta` the
  circumferential position — all radians. `E` in these is elastic modulus
  context per the equations (joint efficiency for membrane), follow the
  inline 4.3.x comments.

## VIII-2 4.4 — external pressure & compressive/combined loading

`Cylinder/Calculations/Div2/Div2Cylinder_external.py` — the most complete
module. Free functions named after Code variables, plus a `get_result(...)`
aggregator that returns a dict of every intermediate and the two pass/fail
checks.

```python
from Cylinder.Calculations.Div2 import Div2Cylinder_external as ext
from Cylinder.Calculations.Div2.Div2Annex3_D import Table3_D_1_Material
from Cylinder.Calculations.Div2 import Div2Cylinder_external as e

res = ext.get_result(
    axial_compression_end_condition=e.AxialCompressionEndCondition.FIXED_FIXED,
    C_m_type=e.CompressionMemberRotationalCoefficient.SIDEWAYS_COMPRESSION,
    P=..., M=..., F=..., V=..., phi=...,   # loads (psi, in·lbf, lbf, lbf, rad)
    D_o=..., t=..., L=...,                 # geometry (in)
    E_y=..., S_y=..., S_u=...,             # modulus, yield, UTS (psi)
    material_type=Table3_D_1_Material.FERRITIC_STEEL,
    M_2=0,
)
res["P_a_"]                 # allowable external pressure (4.4.23)
res["part_h_acceptability"] # shear + hoop compression check -> bool
res["part_i_acceptability"] # axial + bending + shear check -> bool
```

Key standalone functions: `F_he` (elastic hoop buckling, 4.4.17),
`F_ha`/`P_a` (allowable external pressure, 4.4.23–24), `F_xa` (axial, 4.4.58),
`F_va` (shear, 4.4.68), and the combined-loading family `F_xha`/`F_hxa`/
`F_bha`/`F_vha`. Two enums select boundary conditions:
`AxialCompressionEndCondition` (FIXED_FIXED/FIXED_FREE/PINNED_FIXED/
PINNED_PINNED) and `CompressionMemberRotationalCoefficient`.

Several functions raise `CalcExceptions.Div2CylinderException` when a parameter
is outside its valid range (e.g. `D_o/t > 2000` in `C_x`, `lambda_c` bands).
Catch or pre-check ranges and report the limitation rather than crashing.

## VIII-2 4.4.7 — hemispherical head, external pressure

`Cylinder/Calculations/Div2/Div2Hemispherical.py`

- `F_he(E_y, t, R_o)` — elastic buckling stress (4.4.48)
- `F_ha(E_y, R_o, t, sigma_ys, sigma_uts, material_type)` — allowable (4.4.50)
- `P_a(E_y, R_o, t, sigma_ys, sigma_uts, material_type)` — allowable external P (4.4.49)

`material_type` is a `Table3_D_1_Material` enum (see below).

## Material model — `Div2Annex3_D.py` (VIII-2 Annex 3-D)

The buckling functions need an inelastic/tangent-modulus material class:

```python
from Cylinder.Calculations.Div2.Div2Annex3_D import Table3_D_1_Material
# FERRITIC_STEEL, STAINLESS_STEEL_AND_NICKEL_BASE_ALLOYS, DUPLEX_STAINLESS_STEEL,
# PRECIPITATION_HARDENABLE_NICKEL_BASE, ALUMINUM, COPPER, TITANIUM_AND_ZIRCONIUM
```

`Div2Part4_4_general.py` provides the shared `FS(F_ic, S_y)` design-factor
(4.4.1–3) and `F_ic(F_e, E, S_y, S_u, material_type)`, which bisection-solves
the inelastic buckling stress via the Annex 3-D tangent modulus. These are
called internally by the external-pressure functions; you rarely call them
directly.
