"""Validation + regression tests for the calctoys skill harness.

Run:  python tests.py            (or: python -m unittest tests -v)

Two kinds of test:
  * REFERENCE  -- asserts a calc against an independently hand-computed
    closed-form value from the ASME formula. A failure means the engineering
    result changed.
  * REGRESSION/CHARACTERIZATION -- pins current output of code that is not yet
    validated against a published example (e.g. the incomplete App. 2 flange),
    so future edits can't silently change numbers. NOT a correctness claim.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from pv_env import setup, smoke_test  # noqa: E402
import units  # noqa: E402
import report  # noqa: E402

setup()

from Cylinder.Calculations.Div1 import internal_pressure as ug27  # noqa: E402
from Cylinder.Calculations.Div1 import UG32_heads as heads  # noqa: E402
from Cylinder.Calculations.Div2 import Div2Cylinder_internal as div2  # noqa: E402
from Noncircular.Calculations.Appendix13 import (  # noqa: E402
    design_rectangular_unreinforced, design_rectangular_stayed)

TOL = 1e-6


class TestUG27Cylinder(unittest.TestCase):
    """REFERENCE: VIII-1 UG-27 closed form, P=100, D_i=24, S=20000, E=1."""

    def setUp(self):
        p = ug27.UG27params(24.0, 100.0, 20000.0, 1.0, 1.0, 1.0)
        self.c = ug27.UG27Calcs(p)

    def test_hoop_thickness(self):
        # PR/(SE - 0.6P) = 1200/19940
        self.assertAlmostEqual(self.c.min_thk_circ_stress(), 1200 / 19940, delta=TOL)

    def test_longitudinal_thickness(self):
        # PR/(2SE + 0.4P) = 1200/40040
        self.assertAlmostEqual(self.c.min_thk_longitudinal_stress(), 1200 / 40040, delta=TOL)

    def test_design_thickness_governs_hoop(self):
        self.assertAlmostEqual(self.c.design_thickness(), 1200 / 19940, delta=TOL)

    def test_mawp(self):
        # min(circ, long) at t=1.0 -> circ governs = SEt/(R+0.6t) = 20000/12.6
        self.assertAlmostEqual(self.c.max_pressure(), 20000 / 12.6, delta=1e-4)


class TestDiv2Cylinder(unittest.TestCase):
    """REFERENCE: VIII-2 4.3.3 exact form."""

    def test_t_min(self):
        # 0.5 * 48 * (exp(300/20000) - 1)
        expected = 24.0 * (math.exp(0.015) - 1.0)
        self.assertAlmostEqual(div2.t_min(300.0, 20000.0, 1.0, 48.0), expected, delta=TOL)


class TestUG32Heads(unittest.TestCase):
    """REFERENCE: VIII-1 UG-32 formed heads, P=100, S=20000, E=1."""

    P, S, E = 100.0, 20000.0, 1.0

    def test_shape_factor_K_2to1(self):
        self.assertAlmostEqual(heads.K_ellipsoidal(48.0, 12.0), 1.0, delta=TOL)

    def test_shape_factor_M_standard_FandD(self):
        # M = 0.25*(3 + sqrt(48/2.88))
        self.assertAlmostEqual(heads.M_torispherical(48.0, 2.88),
                               0.25 * (3 + math.sqrt(48 / 2.88)), delta=TOL)

    def test_hemispherical(self):
        # PL/(2SE - 0.2P) = 2400/39980
        self.assertAlmostEqual(heads.t_hemispherical(self.P, self.S, self.E, 24.0),
                               2400 / 39980, delta=TOL)

    def test_ellipsoidal_2to1(self):
        # PDK/(2SE - 0.2P), K=1 -> 4800/39980
        self.assertAlmostEqual(heads.t_ellipsoidal(self.P, self.S, self.E, 48.0, h=12.0),
                               4800 / 39980, delta=TOL)

    def test_torispherical(self):
        M = 0.25 * (3 + math.sqrt(48 / 2.88))
        self.assertAlmostEqual(heads.t_torispherical(self.P, self.S, self.E, 48.0, r=2.88),
                               (self.P * 48.0 * M) / 39980, delta=TOL)

    def test_conical(self):
        a = math.radians(20.0)
        expected = (self.P * 48.0) / (2 * math.cos(a) * (self.S * self.E - 0.6 * self.P))
        self.assertAlmostEqual(heads.t_conical(self.P, self.S, self.E, 48.0, a),
                               expected, delta=TOL)

    def test_conical_rejects_steep_angle(self):
        with self.assertRaises(ValueError):
            heads.t_conical(self.P, self.S, self.E, 48.0, math.radians(35.0))

    def test_mawp_roundtrip(self):
        # required_thickness -> P_* should recover the design pressure.
        for kw, pfun in [
            (dict(head_type=heads.HeadType.HEMISPHERICAL, L=24.0),
             lambda t: heads.P_hemispherical(self.S, self.E, t, 24.0)),
            (dict(head_type=heads.HeadType.ELLIPSOIDAL, D=48.0, h=12.0),
             lambda t: heads.P_ellipsoidal(self.S, self.E, t, 48.0, h=12.0)),
            (dict(head_type=heads.HeadType.TORISPHERICAL, L=48.0, r=2.88),
             lambda t: heads.P_torispherical(self.S, self.E, t, 48.0, r=2.88)),
            (dict(head_type=heads.HeadType.CONICAL, D=48.0, alpha=math.radians(20.0)),
             lambda t: heads.P_conical(self.S, self.E, t, 48.0, math.radians(20.0))),
        ]:
            t = heads.required_thickness(P=self.P, S=self.S, E=self.E, **kw)
            self.assertAlmostEqual(pfun(t), self.P, delta=1e-3,
                                   msg=f"round-trip failed for {kw}")


class TestNoncircularAppendix13(unittest.TestCase):
    """REFERENCE (membrane, hand-computed) + CHARACTERIZATION (bending/total)
    for VIII-1 Appendix 13-7(a): unreinforced rectangular vessel,
    h=9.5, H=7.375, P=400, t_1=t_2=0.875, S=20000, E=1."""

    def setUp(self):
        self.r = design_rectangular_unreinforced(
            P=400, S=20000, E=1.0,
            long_side_inside=9.5, short_side_inside=7.375,
            short_side_thickness=0.875, long_side_thickness=0.875)

    def test_membrane_hand_computed(self):
        gm = self.r.governing_membrane
        # SmShort = P h /(2 t_1) = 400*9.5/1.75 = 2171.4286 governs
        self.assertAlmostEqual(gm.membrane, 400 * 9.5 / (2 * 0.875), delta=1e-3)

    def test_allowables(self):
        self.assertEqual(self.r.membrane_allowable, 20000.0)   # 1.0 * S * E
        self.assertEqual(self.r.total_allowable, 30000.0)      # 1.5 * S * E

    def test_governing_total_location_and_value(self):
        gt = self.r.governing_total
        self.assertEqual((gt.label, gt.wall), ("Q_short", "inner"))
        self.assertAlmostEqual(gt.total, 21653.06, delta=0.5)   # characterization

    def test_acceptance_pass(self):
        self.assertTrue(self.r.ok)
        self.assertGreater(self.r.margin(), 0.0)

    def test_acceptance_fail_when_thin(self):
        thin = design_rectangular_unreinforced(
            P=400, S=20000, E=1.0,
            long_side_inside=9.5, short_side_inside=7.375,
            short_side_thickness=0.25, long_side_thickness=0.25)
        self.assertFalse(thin.ok)
        self.assertLess(thin.margin(), 0.0)

    def test_custom_acceptance_factors(self):
        r = design_rectangular_unreinforced(
            P=400, S=20000, E=0.85,
            long_side_inside=9.5, short_side_inside=7.375,
            short_side_thickness=0.875, long_side_thickness=0.875,
            membrane_factor=1.0, bending_factor=1.5)
        self.assertAlmostEqual(r.total_allowable, 1.5 * 20000 * 0.85, delta=1e-6)


class TestNoncircularStayed(unittest.TestCase):
    """REFERENCE (hand-computed from the 13-9(b) equations) for a stay-plate
    rectangular vessel: h=5, H=5, P=100, t_1=1, t_2=2, t_3=0.5, S=20000, E=1.
    With alpha=1, K=8: S_m,short=250, S_m,long=125, S_m,stay=1000,
    S_b_N=-625, S_b_Q_short=1250 -> S_T_N=-375, S_T_Q_short=1500."""

    def setUp(self):
        self.r = design_rectangular_stayed(
            P=100, S=20000, E=1.0,
            stay_pitch=5, short_side_inside=5,
            short_side_thickness=1, long_side_thickness=2,
            stay_plate_thickness=0.5)

    def _point(self, label, wall="inner"):
        return next(p for p in self.r.points if p.label == label and p.wall == wall)

    def test_membrane_values(self):
        self.assertAlmostEqual(self._point("Q_short").membrane, 250.0, delta=1e-6)
        self.assertAlmostEqual(self._point("M").membrane, 125.0, delta=1e-6)   # P H /(2 t_2)
        self.assertAlmostEqual(self._point("stay").membrane, 1000.0, delta=1e-6)

    def test_total_short_midpoint_uses_short_bending(self):
        # Regression for the S_T_N copy-paste bug (was SmShort + S_b_M = 562.5).
        self.assertAlmostEqual(self._point("N").total, -375.0, delta=1e-6)

    def test_total_corner(self):
        self.assertAlmostEqual(self._point("Q_short").total, 1500.0, delta=1e-6)

    def test_stay_is_membrane_only(self):
        sp = self._point("stay")
        self.assertEqual(sp.bending, 0.0)
        self.assertEqual(sp.total, sp.membrane)

    def test_governing_membrane_is_stay(self):
        gm = self.r.governing_membrane
        self.assertEqual(gm.label, "stay")
        self.assertTrue(self.r.ok)


class TestUnits(unittest.TestCase):
    def test_length(self):
        self.assertAlmostEqual(units.to_in(1219.2, "mm"), 48.0, delta=1e-9)
        self.assertAlmostEqual(units.to_in(1.0, "ft"), 12.0, delta=1e-9)

    def test_pressure(self):
        self.assertAlmostEqual(units.to_psi(1.0, "ksi"), 1000.0, delta=1e-9)
        self.assertAlmostEqual(units.to_psi(1.0, "MPa"), 145.0377, delta=1e-3)

    def test_force_and_moment(self):
        self.assertAlmostEqual(units.to_lbf(1.0, "kN"), 224.8089, delta=1e-3)
        self.assertAlmostEqual(units.to_in_lbf(1.0, "N-m"), 8.85075, delta=1e-3)

    def test_unknown_unit_raises(self):
        with self.assertRaises(ValueError):
            units.to_psi(1.0, "furlongs")

    def test_sanity_check_flags_bad_magnitude(self):
        self.assertTrue(units.sanity_check(pressure_psi=2_760_000))   # Pa left unconverted
        self.assertEqual(units.sanity_check(pressure_psi=400.0), [])


class TestReport(unittest.TestCase):
    def test_pass_fail_and_render(self):
        r = (report.CalcReport("t", code="UG-27")
             .input("P", 100.0, "psi")
             .result("t", 0.06, "in")
             .check("ok", True)
             .check("bad", False))
        self.assertFalse(r.all_pass)
        text = r.render()
        self.assertIn("Code basis: UG-27", text)
        self.assertIn("Overall: FAIL", text)
        self.assertIn("UG-27", r.render_markdown())


class TestFlangeCharacterization(unittest.TestCase):
    """REGRESSION (NOT validated): pins the App. 2 flange example outputs so
    edits can't silently change them. See references/flanges.md."""

    def setUp(self):
        # Reuse the worked example's builder.
        import example_flange
        self.f = example_flange.build_flange()

    def test_bolt_load_and_stress_pinned(self):
        self.assertAlmostEqual(self.f.W_m_1, 230295.4, delta=1.0)
        self.assertAlmostEqual(self.f.M_o_operating, 460764.6, delta=1.0)
        self.assertAlmostEqual(self.f.S_H_operating, 24927.3, delta=1.0)
        # Sanity: stresses are positive and finite.
        self.assertGreater(self.f.S_T_operating, 0.0)


class TestImports(unittest.TestCase):
    def test_all_known_good_modules_import(self):
        self.assertEqual(smoke_test(), 0, "some known-good module failed to import")


if __name__ == "__main__":
    unittest.main(verbosity=2)
