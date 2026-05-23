from Cylinder.Calculations.Div1.internal_pressure import UG27params, UG27Calcs


class CylinderDesign:
    """High-level orchestrator for cylindrical shell design checks (UG-27, Div 1)."""

    def __init__(
        self,
        inside_diameter: float,
        allowable_stress: float,
        joint_efficiency_long: float = 1.0,
        joint_efficiency_circ: float = 1.0,
        thickness: float = 0.0,
        internal_pressure: float = 0.0,
    ):
        self.inside_diameter = inside_diameter
        self.allowable_stress = allowable_stress
        self.joint_efficiency_long = joint_efficiency_long
        self.joint_efficiency_circ = joint_efficiency_circ
        self.thickness = thickness
        self.internal_pressure = internal_pressure

    def _ug27(self) -> UG27Calcs:
        params = UG27params(
            inside_diameter=self.inside_diameter,
            internal_pressure=self.internal_pressure,
            allowable_stress=self.allowable_stress,
            joint_efficiency_long=self.joint_efficiency_long,
            joint_efficiency_circ=self.joint_efficiency_circ,
            thickness=self.thickness,
        )
        return UG27Calcs(params)

    def required_thickness(self) -> float:
        """Minimum required wall thickness per UG-27."""
        return self._ug27().design_thickness()

    def max_allowable_pressure(self) -> float:
        """Maximum allowable working pressure for the current thickness per UG-27."""
        return self._ug27().max_pressure()

    def is_adequate(self) -> bool:
        """True if the supplied thickness satisfies UG-27 for the design pressure."""
        return self.thickness >= self.required_thickness()

    def report(self) -> dict:
        """Return a summary of all key design results."""
        calcs = self._ug27()
        req_t = calcs.design_thickness()
        return {
            "inside_diameter": self.inside_diameter,
            "thickness": self.thickness,
            "internal_pressure": self.internal_pressure,
            "allowable_stress": self.allowable_stress,
            "joint_efficiency_long": self.joint_efficiency_long,
            "joint_efficiency_circ": self.joint_efficiency_circ,
            "required_thickness": req_t,
            "max_allowable_pressure": calcs.max_pressure(),
            "is_adequate": self.thickness >= req_t,
        }
