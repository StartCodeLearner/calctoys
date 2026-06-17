import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cylinder.Cylinder import CylinderDesign


def _sticky_all():
    return tk.N + tk.E + tk.W + tk.S


class UG27Panel(tk.LabelFrame):
    """Input/output panel for ASME UG-27 cylindrical shell checks."""

    _FIELDS = [
        ("Inside Diameter (in)",      "inside_diameter",      "24.0"),
        ("Internal Pressure (psi)",   "internal_pressure",    "100.0"),
        ("Allowable Stress (psi)",    "allowable_stress",     "20000.0"),
        ("Joint Eff. (longitudinal)", "joint_efficiency_long", "1.0"),
        ("Joint Eff. (circumferential)", "joint_efficiency_circ", "1.0"),
        ("Wall Thickness (in)",       "thickness",            "0.5"),
    ]

    def __init__(self, parent):
        tk.LabelFrame.__init__(self, parent, text="UG-27  —  Cylindrical Shell (Div 1)")
        self._vars = {}
        self._build_inputs()
        self._build_button()
        self._build_output()

    def _build_inputs(self):
        for row, (label, key, default) in enumerate(self._FIELDS):
            tk.Label(self, text=label).grid(row=row, column=0, sticky=tk.W, padx=6, pady=3)
            var = tk.StringVar(value=default)
            tk.Entry(self, textvariable=var, width=12).grid(row=row, column=1, sticky=tk.W, padx=6, pady=3)
            self._vars[key] = var

    def _build_button(self):
        row = len(self._FIELDS)
        tk.Button(self, text="Calculate", command=self._run).grid(
            row=row, column=0, columnspan=2, pady=8
        )

    def _build_output(self):
        self._output = tk.StringVar(value="Enter values and press Calculate.")
        tk.Label(
            self, textvariable=self._output, justify=tk.LEFT,
            font=("Courier", 10), wraplength=320,
        ).grid(row=len(self._FIELDS) + 1, column=0, columnspan=2, sticky=tk.W, padx=6, pady=4)

    def _run(self):
        try:
            vals = {k: float(v.get()) for k, v in self._vars.items()}
            design = CylinderDesign(**vals)
            r = design.report()
            status = "PASS ✅" if r["is_adequate"] else "FAIL ❌"
            self._output.set(
                f"Required thickness :  {r['required_thickness']:.4f} in\n"
                f"Max allow. pressure:  {r['max_allowable_pressure']:.1f} psi\n"
                f"Adequacy check     :  {status}"
            )
        except ValueError as exc:
            self._output.set(f"Input error: {exc}")


class MainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        UG27Panel(self).grid(row=0, column=0, sticky=_sticky_all(), padx=10, pady=10)


def init_ui(context=None):
    root = tk.Tk()
    root.title("calctoys — Pressure Vessel Calculators")
    MainWindow(root).grid(row=0, column=0, sticky=_sticky_all())
    root.mainloop()
