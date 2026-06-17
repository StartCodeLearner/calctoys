"""Structured, audit-ready calc reports for calctoys results.

A CalcReport collects the four things an engineer needs to check a hand calc:
the Code basis, the inputs, the intermediate values, and the governing result
with a pass/fail verdict. Render it to plain text or Markdown.

Example:
    r = CalcReport("Shell thickness", code="ASME VIII-1 UG-27(c)(1)")
    r.input("P", 100, "psi", "internal pressure")
    r.input("S", 20000, "psi", "allowable stress")
    r.intermediate("R", 12.0, "in", "inside radius")
    r.result("t_required", 0.0602, "in", "minimum required thickness")
    r.check("t_provided >= t_required", 0.25 >= 0.0602)
    print(r.render())          # plain text
    print(r.render_markdown())  # Markdown
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class _Row:
    name: str
    value: object
    unit: str = ""
    note: str = ""

    def fmt_value(self) -> str:
        v = self.value
        if isinstance(v, float):
            return f"{v:.6g}"
        return str(v)


@dataclass
class _Check:
    description: str
    passed: bool
    detail: str = ""


@dataclass
class CalcReport:
    title: str
    code: str = ""
    inputs: list = field(default_factory=list)
    intermediates: list = field(default_factory=list)
    results: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    # --- builders (chainable) ---
    def input(self, name, value, unit="", note=""):
        self.inputs.append(_Row(name, value, unit, note))
        return self

    def intermediate(self, name, value, unit="", note=""):
        self.intermediates.append(_Row(name, value, unit, note))
        return self

    def result(self, name, value, unit="", note=""):
        self.results.append(_Row(name, value, unit, note))
        return self

    def check(self, description, passed, detail=""):
        self.checks.append(_Check(description, bool(passed), detail))
        return self

    def note(self, text):
        self.notes.append(text)
        return self

    @property
    def all_pass(self) -> bool:
        return all(c.passed for c in self.checks)

    # --- rendering ---
    def _rows_text(self, rows) -> list[str]:
        if not rows:
            return ["  (none)"]
        w = max(len(r.name) for r in rows)
        out = []
        for r in rows:
            line = f"  {r.name:<{w}} = {r.fmt_value()}"
            if r.unit:
                line += f" {r.unit}"
            if r.note:
                line += f"   # {r.note}"
            out.append(line)
        return out

    def render(self) -> str:
        L = [self.title]
        if self.code:
            L.append(f"Code basis: {self.code}")
        L.append("")
        L.append("Inputs:")
        L += self._rows_text(self.inputs)
        if self.intermediates:
            L.append("")
            L.append("Intermediates:")
            L += self._rows_text(self.intermediates)
        L.append("")
        L.append("Results:")
        L += self._rows_text(self.results)
        if self.checks:
            L.append("")
            L.append("Checks:")
            for c in self.checks:
                tag = "PASS" if c.passed else "FAIL"
                line = f"  [{tag}] {c.description}"
                if c.detail:
                    line += f"   ({c.detail})"
                L.append(line)
            L.append("")
            L.append(f"Overall: {'PASS' if self.all_pass else 'FAIL'}")
        if self.notes:
            L.append("")
            L.append("Notes:")
            L += [f"  - {n}" for n in self.notes]
        return "\n".join(L)

    def _rows_md(self, rows) -> list[str]:
        out = ["| Name | Value | Unit | Note |", "|---|---|---|---|"]
        if not rows:
            out.append("| _(none)_ | | | |")
        for r in rows:
            out.append(f"| `{r.name}` | {r.fmt_value()} | {r.unit} | {r.note} |")
        return out

    def render_markdown(self) -> str:
        L = [f"## {self.title}"]
        if self.code:
            L.append(f"**Code basis:** {self.code}")
        L.append("")
        L.append("**Inputs**")
        L += self._rows_md(self.inputs)
        if self.intermediates:
            L.append("")
            L.append("**Intermediates**")
            L += self._rows_md(self.intermediates)
        L.append("")
        L.append("**Results**")
        L += self._rows_md(self.results)
        if self.checks:
            L.append("")
            L.append("**Checks**")
            for c in self.checks:
                tag = "✅ PASS" if c.passed else "❌ FAIL"
                detail = f" — {c.detail}" if c.detail else ""
                L.append(f"- {tag}: {c.description}{detail}")
            L.append("")
            L.append(f"**Overall: {'PASS' if self.all_pass else 'FAIL'}**")
        if self.notes:
            L.append("")
            L.append("**Notes**")
            L += [f"- {n}" for n in self.notes]
        return "\n".join(L)


if __name__ == "__main__":
    r = (CalcReport("Shell thickness", code="ASME VIII-1 UG-27(c)(1)")
         .input("P", 100.0, "psi", "internal pressure")
         .input("S", 20000.0, "psi", "allowable stress")
         .input("E", 1.0, "", "joint efficiency")
         .intermediate("R", 12.0, "in", "inside radius")
         .result("t_required", 0.0602, "in", "minimum required thickness")
         .check("t_provided (0.25) >= t_required", 0.25 >= 0.0602, "0.25 in nominal")
         .note("Thin-wall UG-27 form; verify P <= 0.385 S E."))
    print(r.render())
    print("\n--- markdown ---\n")
    print(r.render_markdown())
