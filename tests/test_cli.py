import io
import json
import os
import subprocess
import sys

import pytest

import cli


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(REPO_ROOT, "src", "cli.py")


def _run_cli(args, capsys):
    rc = cli.main(args)
    captured = capsys.readouterr()
    return rc, captured.out, captured.err


def test_no_args_prints_usage_and_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main([])
    assert excinfo.value.code != 0


def test_list_command_human_output(capsys):
    rc, out, _ = _run_cli(["list"], capsys)
    assert rc == 0
    assert "cylinder ug27" in out
    assert "cylinder div2-tmin" in out
    assert "flange appendix24-demo" in out


def test_list_command_json_output(capsys):
    rc, out, _ = _run_cli(["list", "--json"], capsys)
    assert rc == 0
    payload = json.loads(out)
    assert isinstance(payload, list) and payload
    commands = {entry["command"] for entry in payload}
    assert "cylinder ug27" in commands


def test_cylinder_ug27_json(capsys):
    rc, out, _ = _run_cli(
        [
            "cylinder", "ug27",
            "--inside-diameter", "24",
            "--internal-pressure", "100",
            "--allowable-stress", "20000",
            "--joint-efficiency-long", "1",
            "--joint-efficiency-circ", "1",
            "--thickness", "1",
            "--json",
        ],
        capsys,
    )
    assert rc == 0
    data = json.loads(out)
    assert set(data) >= {"design_thickness", "max_pressure"}
    assert data["design_thickness"] > 0
    assert data["max_pressure"] > 0


def test_cylinder_div2_tmin_json(capsys):
    rc, out, _ = _run_cli(
        ["cylinder", "div2-tmin", "--P", "100", "--S", "20000",
         "--E", "1.0", "--D-i", "24", "--json"],
        capsys,
    )
    assert rc == 0
    data = json.loads(out)
    assert data["t_min"] > 0


def test_cylinder_div2_hoop_cylinder(capsys):
    rc, out, _ = _run_cli(
        ["cylinder", "div2-hoop", "--shell-type", "cylinder",
         "--P", "100", "--E", "1.0", "--D", "24", "--D-o", "26", "--json"],
        capsys,
    )
    assert rc == 0
    data = json.loads(out)
    assert data["sigma_theta_m"] == pytest.approx((100 * 24) / (1.0 * (26 - 24)))


def test_cylinder_div2_fs(capsys):
    rc, out, _ = _run_cli(
        ["cylinder", "div2-fs", "--F-ic", "10000", "--S-y", "30000", "--json"],
        capsys,
    )
    assert rc == 0
    assert json.loads(out)["FS"] == 2.0


def test_cylinder_div2_hemi(capsys):
    rc, out, _ = _run_cli(
        [
            "cylinder", "div2-hemi",
            "--E-y", "29000000", "--R-o", "60", "--t", "0.5",
            "--sigma-ys", "30000", "--sigma-uts", "60000",
            "--material-type", "ferritic_steel", "--json",
        ],
        capsys,
    )
    assert rc == 0
    data = json.loads(out)
    assert data["F_he"] > 0
    assert data["P_a"] > 0


def test_flange_appendix24_demo_runs(capsys):
    rc, out, _ = _run_cli(["flange", "appendix24-demo", "--json"], capsys)
    assert rc == 0
    data = json.loads(out)
    # Spot-check a few result keys produced by the clamped-flange assembly.
    assert {"N_bolts", "G", "W", "hub", "clamp"} <= set(data)
    assert data["N_bolts"] == 4


def test_tubesheet_uhx11_json(capsys):
    rc, out, _ = _run_cli(
        [
            "tubesheet", "uhx11",
            "--r-o", "30", "--d-t", "1.0", "--t-t", "0.083",
            "--Et", "26900000", "--E", "26900000",
            "--St", "13400", "--S", "19000",
            "--p", "1.25", "--A-L", "99", "--c-t", "0.5",
            "--h", "5", "--l-tx", "5", "--pitch-type", "square", "--json",
        ],
        capsys,
    )
    assert rc == 0
    data = json.loads(out)
    assert data["D_o"] == pytest.approx(61.0)
    assert 0.0 < data["E_star_ratio"] < 1.0


def test_list_includes_tubesheet(capsys):
    rc, out, _ = _run_cli(["list"], capsys)
    assert rc == 0
    assert "tubesheet uhx11" in out


def test_cli_invokable_as_script():
    # End-to-end smoke: ensure the script entry point works the way a user
    # would actually invoke it.
    result = subprocess.run(
        [sys.executable, CLI_PATH, "list", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert any(entry["command"] == "ui" for entry in payload)
