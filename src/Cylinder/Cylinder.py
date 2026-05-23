"""Unified cylindrical shell design helper (ASME BPVC Div 1, UG-27)."""
from dataclasses import dataclass
from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


@dataclass
class CylinderDesign:
    """All inputs needed to size or rate a cylindrical pressure-vessel shell."""
    inside_diameter: float
    design_pressure: float
    allowable_stress: float
    joint_efficiency_long: float = 1.0
    joint_efficiency_circ: float = 1.0
    corrosion_allowance: float = 0.0

    def _calcs(self, nominal_thickness: float = 0.0) -> UG27Calcs:
        net_thickness = max(nominal_thickness - self.corrosion_allowance, 0.0)
        return UG27Calcs(UG27params(
            inside_diameter=self.inside_diameter,
            internal_pressure=self.design_pressure,
            allowable_stress=self.allowable_stress,
            joint_efficiency_long=self.joint_efficiency_long,
            joint_efficiency_circ=self.joint_efficiency_circ,
            thickness=net_thickness,
        ))

    def required_thickness(self) -> float:
        """Minimum required net wall thickness (no corrosion allowance added)."""
        return self._calcs().design_thickness()

    def required_nominal_thickness(self) -> float:
        """Minimum nominal thickness including corrosion allowance."""
        return self.required_thickness() + self.corrosion_allowance

    def mawp(self, nominal_thickness: float) -> float:
        """Maximum allowable working pressure for a given nominal thickness."""
        return self._calcs(nominal_thickness).max_pressure()

    def is_adequate(self, nominal_thickness: float) -> bool:
        """Return True if the nominal thickness satisfies the design pressure."""
        return self.mawp(nominal_thickness) >= self.design_pressure
