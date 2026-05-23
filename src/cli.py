"""Unified command-line interface for calctoys.

Exposes the working portions of the codebase under a single entry point. Run
``python src/cli.py --help`` for a list of sub-commands, or ``python src/cli.py
list`` to see every calculation registered with the CLI.

The script adds its own directory to ``sys.path`` so submodules can be imported
the same way they are inside the project (``from Cylinder.Calculations...``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


# --- output helpers ---------------------------------------------------------


def _emit(result: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, default=str, indent=2))
        return
    if isinstance(result, dict):
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        print(result)


# --- command handlers -------------------------------------------------------


def cmd_ui(args: argparse.Namespace) -> int:
    from ui import ui as ui_mod
    ui_mod.init_ui()
    return 0


def cmd_cylinder_ug27(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs

    params = UG27params(
        inside_diameter=args.inside_diameter,
        internal_pressure=args.internal_pressure,
        allowable_stress=args.allowable_stress,
        joint_efficiency_long=args.joint_efficiency_long,
        joint_efficiency_circ=args.joint_efficiency_circ,
        thickness=args.thickness,
    )
    calc = UG27Calcs(params)
    result = {
        "design_thickness": calc.design_thickness(),
        "min_thk_circ_stress": calc.min_thk_circ_stress(),
        "min_thk_longitudinal_stress": calc.min_thk_longitudinal_stress(),
        "max_pressure": calc.max_pressure(),
        "max_pressure_circ_stress": calc.max_pressure_circ_stress(),
        "max_pressure_longitudinal_stress": calc.max_pressure_longitudinal_stress(),
    }
    _emit(result, args.json)
    return 0


def cmd_cylinder_div2_tmin(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div2 import Div2Cylinder_internal as DC
    _emit({"t_min": DC.t_min(args.P, args.S, args.E, args.D_i)}, args.json)
    return 0


def cmd_cylinder_div2_hoop(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div2 import Div2Cylinder_internal as DC
    shell = DC.ShellType[args.shell_type.upper()]
    val = DC.sigma_theta_m(shell, args.P, args.E, args.D, args.D_o, args.alpha)
    _emit({"sigma_theta_m": val}, args.json)
    return 0


def cmd_cylinder_div2_hemi_p_a(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div2 import Div2Hemispherical as DH
    from Cylinder.Calculations.Div2.Div2Annex3_D import Table3_D_1_Material

    material_type = Table3_D_1_Material[args.material_type.upper()]
    result = {
        "F_he": DH.F_he(args.E_y, args.t, args.R_o),
        "F_ha": DH.F_ha(args.E_y, args.R_o, args.t, args.sigma_ys, args.sigma_uts, material_type),
        "P_a": DH.P_a(args.E_y, args.R_o, args.t, args.sigma_ys, args.sigma_uts, material_type),
    }
    _emit(result, args.json)
    return 0


def cmd_cylinder_div2_ext_pressure(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div2 import Div2Cylinder_external as DE
    from Cylinder.Calculations.Div2.Div2Annex3_D import Table3_D_1_Material

    material_type = Table3_D_1_Material[args.material_type.upper()]
    result = {
        "F_he": DE.F_he(args.E_y, args.D_o, args.t, args.L),
        "F_ha": DE.F_ha(args.D_o, args.t, args.L, args.E_y, args.sigma_ys, args.sigma_uts, material_type),
        "P_a": DE.P_a(args.E_y, args.D_o, args.t, args.L, args.sigma_ys, args.sigma_uts, material_type),
    }
    _emit(result, args.json)
    return 0


def cmd_cylinder_div2_fs(args: argparse.Namespace) -> int:
    from Cylinder.Calculations.Div2 import Div2Part4_4_general as DG
    _emit({"FS": DG.FS(args.F_ic, args.S_y)}, args.json)
    return 0


def cmd_flange_appendix24_demo(args: argparse.Namespace) -> int:
    try:
        from Flange.Clamped.Appendix24 import (
            DesignCondition, Material, Bolting, Hub, Clamp, Gasket, HubAndClamp,
        )
    except ImportError as exc:
        print(f"Flange.Clamped.Appendix24 is currently unimportable: {exc}", file=sys.stderr)
        return 2

    condition = DesignCondition(
        is_operating=True, temperature=200, ambient_temperature=75,
        pressure=3000, bolting_is_controlled=False, has_retainer=False,
    )
    bolt = Bolting(material=Material(1), diameter=1.75, root_area=1.98)
    left_hub = Hub(
        sketch=Hub.Sketch.c, material=Material(2),
        outside_diameter=(18 + (12.75 + 2.75) * 2), inner_diameter=18,
        hub_cross_section_corner_radius=0.25, small_end_thickness=12.75,
        length_of_small_end=15, taper_length=2.75, neck_length=15,
        neck_thickness_at_shoulder=12.75, shoulder_thickness=7.321,
        shoulder_height=2.75, transition_angle=10, shoulder_angle=10,
        friction_angle=5,
    )
    clamp = Clamp(
        sketch=Clamp.Sketch.a, material=Material(3), bolt_circle_radius=32.25,
        clamp_inside_diameter=43.75, clamp_width=28,
        effective_clamp_thickness=7.625, effective_clamp_gap=14,
        corner_radius=0.25, distance_from_bolt_circle_to_clamp_od=3.7,
        effective_lip_length=2.75, lug_height=15, lug_width=28,
    )
    gasket = Gasket(outer_diameter=20, inner_diameter=18, gasket_factor=0, seating_stress=0)
    assy = HubAndClamp(
        design_data=condition, bolting=bolt, gasket=gasket, hub=left_hub, clamp=clamp,
    )
    _emit(assy.get_result(), args.json)
    return 0


# Registry of "available" calcs, surfaced via the `list` command.
CALC_REGISTRY: list[dict[str, str]] = [
    {"command": "ui", "description": "Launch the Tk-based UI shell"},
    {"command": "cylinder ug27", "description": "ASME VIII-1 UG-27 cylindrical shell under internal pressure"},
    {"command": "cylinder div2-tmin", "description": "ASME VIII-2 4.3.3.1 minimum thickness for a cylinder"},
    {"command": "cylinder div2-hoop", "description": "ASME VIII-2 4.3.10 mean hoop stress (cylinder/sphere/cone)"},
    {"command": "cylinder div2-hemi", "description": "ASME VIII-2 4.4.7.1 hemispherical head under external pressure"},
    {"command": "cylinder div2-ext-pressure", "description": "ASME VIII-2 4.4.5.1 cylinder under external pressure"},
    {"command": "cylinder div2-fs", "description": "ASME VIII-2 4.4.2 buckling safety factor"},
    {"command": "flange appendix24-demo", "description": "Run the bundled Appendix 24 clamped-flange demo"},
]


def cmd_list(args: argparse.Namespace) -> int:
    if args.json:
        _emit(CALC_REGISTRY, True)
        return 0
    width = max(len(c["command"]) for c in CALC_REGISTRY)
    for c in CALC_REGISTRY:
        print(f"  {c['command']:<{width}}  {c['description']}")
    return 0


# --- argument parsing -------------------------------------------------------


def _add_json_flag(p: argparse.ArgumentParser) -> None:
    p.add_argument("--json", action="store_true", help="emit results as JSON")


_MATERIAL_CHOICES = [
    "ferritic_steel",
    "stainless_steel_and_nickel_base_alloys",
    "duplex_stainless_steel",
    "precipitation_hardenable_nickel_base",
    "aluminum",
    "copper",
    "titanium_and_zirconium",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calctoys",
        description="Pressure vessel calculation toolbox (ASME BPVC).",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    # ui
    p_ui = sub.add_parser("ui", help="launch the Tk UI")
    p_ui.set_defaults(func=cmd_ui)

    # list
    p_list = sub.add_parser("list", help="list available calculations")
    _add_json_flag(p_list)
    p_list.set_defaults(func=cmd_list)

    # cylinder group
    p_cyl = sub.add_parser("cylinder", help="cylindrical shell calculations")
    cyl_sub = p_cyl.add_subparsers(dest="cylinder_command", required=True, metavar="<sub>")

    p_ug27 = cyl_sub.add_parser("ug27", help="ASME VIII-1 UG-27 internal-pressure shell")
    p_ug27.add_argument("--inside-diameter", type=float, required=True)
    p_ug27.add_argument("--internal-pressure", type=float, required=True)
    p_ug27.add_argument("--allowable-stress", type=float, required=True)
    p_ug27.add_argument("--joint-efficiency-long", type=float, default=1.0)
    p_ug27.add_argument("--joint-efficiency-circ", type=float, default=1.0)
    p_ug27.add_argument("--thickness", type=float, required=True)
    _add_json_flag(p_ug27)
    p_ug27.set_defaults(func=cmd_cylinder_ug27)

    p_tmin = cyl_sub.add_parser("div2-tmin", help="VIII-2 4.3.3.1 minimum thickness")
    p_tmin.add_argument("--P", type=float, required=True, help="internal pressure")
    p_tmin.add_argument("--S", type=float, required=True, help="allowable stress")
    p_tmin.add_argument("--E", type=float, default=1.0, help="joint efficiency")
    p_tmin.add_argument("--D-i", dest="D_i", type=float, required=True, help="inside diameter")
    _add_json_flag(p_tmin)
    p_tmin.set_defaults(func=cmd_cylinder_div2_tmin)

    p_hoop = cyl_sub.add_parser("div2-hoop", help="VIII-2 4.3.10 mean hoop stress")
    p_hoop.add_argument("--shell-type", choices=["cylinder", "spherical", "conical"], required=True)
    p_hoop.add_argument("--P", type=float, required=True)
    p_hoop.add_argument("--E", type=float, default=1.0)
    p_hoop.add_argument("--D", type=float, required=True)
    p_hoop.add_argument("--D-o", dest="D_o", type=float, required=True)
    p_hoop.add_argument("--alpha", type=float, default=0.0, help="cone half-angle (rad)")
    _add_json_flag(p_hoop)
    p_hoop.set_defaults(func=cmd_cylinder_div2_hoop)

    p_hemi = cyl_sub.add_parser("div2-hemi", help="VIII-2 4.4.7.1 hemi external pressure")
    p_hemi.add_argument("--E-y", dest="E_y", type=float, required=True, help="Young's modulus")
    p_hemi.add_argument("--R-o", dest="R_o", type=float, required=True, help="outside radius")
    p_hemi.add_argument("--t", type=float, required=True, help="thickness")
    p_hemi.add_argument("--sigma-ys", dest="sigma_ys", type=float, required=True)
    p_hemi.add_argument("--sigma-uts", dest="sigma_uts", type=float, required=True)
    p_hemi.add_argument("--material-type", required=True, choices=_MATERIAL_CHOICES)
    _add_json_flag(p_hemi)
    p_hemi.set_defaults(func=cmd_cylinder_div2_hemi_p_a)

    p_ext = cyl_sub.add_parser("div2-ext-pressure", help="VIII-2 4.4.5.1 cylinder under external pressure")
    p_ext.add_argument("--E-y", dest="E_y", type=float, required=True, help="Young's modulus")
    p_ext.add_argument("--D-o", dest="D_o", type=float, required=True, help="outside diameter")
    p_ext.add_argument("--t", type=float, required=True, help="wall thickness")
    p_ext.add_argument("--L", type=float, required=True, help="unsupported length")
    p_ext.add_argument("--sigma-ys", dest="sigma_ys", type=float, required=True)
    p_ext.add_argument("--sigma-uts", dest="sigma_uts", type=float, required=True)
    p_ext.add_argument("--material-type", required=True, choices=_MATERIAL_CHOICES)
    _add_json_flag(p_ext)
    p_ext.set_defaults(func=cmd_cylinder_div2_ext_pressure)

    p_fs = cyl_sub.add_parser("div2-fs", help="VIII-2 4.4.2 buckling safety factor")
    p_fs.add_argument("--F-ic", dest="F_ic", type=float, required=True)
    p_fs.add_argument("--S-y", dest="S_y", type=float, required=True)
    _add_json_flag(p_fs)
    p_fs.set_defaults(func=cmd_cylinder_div2_fs)

    # flange group
    p_fl = sub.add_parser("flange", help="flange calculations")
    fl_sub = p_fl.add_subparsers(dest="flange_command", required=True, metavar="<sub>")
    p_a24 = fl_sub.add_parser(
        "appendix24-demo", help="run the bundled Appendix 24 demo (currently broken upstream)",
    )
    _add_json_flag(p_a24)
    p_a24.set_defaults(func=cmd_flange_appendix24_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func: Callable[[argparse.Namespace], int] = args.func
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
