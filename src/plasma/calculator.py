"""Plasma calculation primitives and default reactor conditions.

This module stores the baseline constants and chamber conditions taken from
the Excel reference sheet. Values are normalized to SI units so the plasma
and SPICE layers can share the same inputs without repeated unit conversion.
"""

from dataclasses import dataclass, field
from math import pi


TORR_TO_PA = 133.32236842105263
MM_TO_M = 1e-3


@dataclass(frozen=True)
class BasicConstants:
    """Physical constants used by the plasma model."""

    boltzmann_constant: float = 1.38065e-23
    vacuum_permittivity: float = 8.85e-12
    electron_charge: float = 1.6e-19
    electron_mass: float = 9.1095e-31
    argon_mass: float = 6.6335e-26
    excitation_energy_ev: float = 12.14
    ionization_energy_ev: float = 15.76

# @dataclass는 데이터 담는 클래스를 짧고 편하게 해준다.
# @dataclass => __init__, __repr__, __eq__ 등등의 메서드를 자동으로 만들어준다.
# frozen=True => 객체가 불변이 되도록 해준다. 즉, 객체가 생성된 후에는 속성 값을 변경할 수 없다.

@dataclass(frozen=True)
class ChamberConditions:
    """Default chamber geometry and operating point."""

    chamber_height_m: float = 5.679328897 * MM_TO_M
    chamber_radius_m: float = 238.438997 * MM_TO_M
    pressure_torr: float = 3.5
    temperature_k: float = 423.0

# @property는 method를 property처럼 표현하게 해준다 
# ex) obj.value() -> obj.value

    @property   
    def chamber_height_mm(self) -> float:
        return self.chamber_height_m / MM_TO_M

    @property
    def chamber_radius_mm(self) -> float:
        return self.chamber_radius_m / MM_TO_M

    @property
    def chamber_volume_m3(self) -> float:
        return pi * (self.chamber_radius_m ** 2) * self.chamber_height_m

    @property
    def pressure_pa(self) -> float:
        return self.pressure_torr * TORR_TO_PA


@dataclass
class PlasmaCalculator:
    """Container for plasma-side calculations."""

    gas: str = "argon"
    constants: BasicConstants = field(default_factory=BasicConstants)
    chamber: ChamberConditions = field(default_factory=ChamberConditions)

    def compute_impedance(self, voltage: complex, current: complex) -> complex:
        """Return impedance from voltage and current."""
        if current == 0:
            raise ValueError("Current must be non-zero.")
        return voltage / current

    def compute_power_density(self, power: float, volume: float | None = None) -> float:
        """Return power density using the supplied or default chamber volume."""
        effective_volume = volume if volume is not None else self.chamber.chamber_volume_m3
        if effective_volume == 0:
            raise ValueError("Volume must be non-zero.")
        return power / effective_volume
