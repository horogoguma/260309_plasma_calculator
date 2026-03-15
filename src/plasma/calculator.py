"""Plasma calculation primitives and default reactor conditions.

This module stores the baseline constants and chamber conditions taken from
the Excel reference sheet. Values are normalized to SI units so the plasma
and SPICE layers can share the same inputs without repeated unit conversion.
"""

from dataclasses import dataclass
from math import pi
from math import exp
import math

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


class PlasmaCalculator:
    """Container for plasma-side calculations."""

    def __init__(
        self,
        gas: str = "argon",
        constants: BasicConstants | None = None,
        chamber: ChamberConditions | None = None,
        electron_temperature_ev: float = 2.0,
        sheath_voltage: float = 100.0,
        RF_power: float = 1000.0,
    ) -> None:
        self.gas = gas
        self.constants = constants if constants is not None else BasicConstants()
        self.chamber = chamber if chamber is not None else ChamberConditions()
        self.electron_temperature_ev = electron_temperature_ev
        self.sheath_voltage = sheath_voltage
        self.RF_power = RF_power

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
    
    def compute_ion_mean_free_path(self, pressure_torr: float | None = None) -> float:
        """Return ion mean free path from chamber pressure in torr."""
        effective_pressure = (
            pressure_torr if pressure_torr is not None else self.chamber.pressure_torr
        )
        if effective_pressure == 0:
            raise ValueError("Chamber pressure must be non-zero.")
        return effective_pressure / 330
    
    def compute_gas_number_density(self, pressure_pa: float | None = None, temperature_k: float | None = None) -> float:
        """Return gas number density from pressure in Pa and temperature in K."""
        effective_pressure = pressure_pa if pressure_pa is not None else self.chamber.pressure_pa
        effective_temperature = temperature_k if temperature_k is not None else self.chamber.temperature_k
        return effective_pressure / (self.constants.boltzmann_constant * effective_temperature)
    
    def compute_effective_area(self, chamber_radius_m: float | None = None, chamber_height_m: float | None = None) -> float:
        """Return effective area from chamber radius in m."""
        effective_radius = chamber_radius_m if chamber_radius_m is not None else self.chamber.chamber_radius_m
        effective_height = chamber_height_m if chamber_height_m is not None else self.chamber.chamber_height_m
        if effective_radius == 0:
            raise ValueError("Chamber radius must be non-zero.")
        return 2 * pi * effective_radius * effective_radius * 0.61 + 2 * pi * effective_radius * effective_height * 0.61
    
    def compute_effective_length(self, chamber_radius_m: float | None = None, chamber_height_m: float | None = None) -> float:
        """Return effective length from chamber height in m."""
        effective_radius = chamber_radius_m if chamber_radius_m is not None else self.chamber.chamber_radius_m
        effective_height = chamber_height_m if chamber_height_m is not None else self.chamber.chamber_height_m
        if effective_height == 0:
            raise ValueError("Chamber height must be non-zero.")
        return pi * effective_radius * effective_radius * effective_height / 0.61

    def compute_elastic_collision_constant(self, electron_temperature_ev: float | None = None) -> float:
        """Return elastic collision constant.""" 
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        return (0.00000000000002336)*(electron_temperature_ev**1.609)*(math.exp(0.0618*((math.log(electron_temperature_ev))**(2))-0.117*((math.log(electron_temperature_ev))**(3))))
    
    def compute_exitation_collision_constant(self, electron_temperature_ev: float | None = None) -> float:
        """Return excitation collision constant."""
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        return (0.0000000000000248)*((electron_temperature_ev)**(0.33))*(math.exp(-12.78/electron_temperature_ev))
    
    def compute_ionization_collision_constant(self, electron_temperature_ev: float | None = None) -> float:
        """Return ionization collision constant."""
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        return (0.0000000000000012)*((electron_temperature_ev)**(0.59))*(math.exp(-17.44/electron_temperature_ev))
    
    def compute_number_need_to_be_zero(self, ionization_energy_ev: float | None = None, electron_temperature_ev: float | None = None) -> float:
        """Return electron temperature in eV from excitation and ionization energies."""
        effective_ionization_energy = ionization_energy_ev if ionization_energy_ev is not None else self.constants.ionization_energy_ev
        
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev

        if electron_temperature_ev <= 0:
            raise ValueError("electron_temperature_ev must be positive.")

        if electron_temperature_ev < 0.1 or electron_temperature_ev > 100:
            raise ValueError("electron_temperature_ev is out of allowed range.")

        return (
            self.compute_ionization_collision_constant(self.electron_temperature_ev)
            * self.compute_gas_number_density(self.chamber.pressure_pa, self.chamber.temperature_k)
            * self.compute_effective_length(self.chamber.chamber_radius_m, self.chamber.chamber_height_m)
            / self.compute_bohm_velocity(self.electron_temperature_ev)
        )
    
    def compute_bohm_velocity(self, electron_temperature_ev: float | None = None) -> float:
        """Return Bohm velocity from electron temperature in eV."""
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        return (self.constants.electron_charge * electron_temperature_ev / self.constants.ion_mass) ** 0.5
    
    def compute_electron_collision_energy_loss(self, electron_temperature_ev: float | None = None) -> float:
        """Return electron collision energy loss from electron temperature in eV."""
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        return(
            (
                self.compute_elastic_collision_constant(electron_temperature_ev) * (3 * self.constans.electron_mass / self.constants.argon_mass) * self.electron_temperature_ev  
                + self.compute_exitation_collision_constant(electron_temperature_ev) * self.constants.excitation_energy_ev
                * self.compute_ionization_collision_constant(electron_temperature_ev) * self.constants.ionization_energy_ev
            ) / self.self.compute_ionization_collision_constant(electron_temperature_ev)
        )

    def compute_electron_ion_energy_loss(self, electron_temperature_ev: float | None = None, sheath_voltage: float | None = None) -> float:
        """Return electron-ion energy loss from electron temperature in eV."""
        if sheath_voltage is None:
            sheath_voltage = self.sheath_voltage
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev    
        return (
            (
                sheath_voltage + (3/2) * electron_temperature_ev
            )
        )
    
    def compute_total_energy_loss(self, electron_temperature_ev: float | None = None, sheath_voltage: float | None = None) -> float:
        """Return total energy loss from electron temperature in eV."""
        if electron_temperature_ev is None:
            electron_temperature_ev = self.electron_temperature_ev
        if sheath_voltage is None:
            sheath_voltage = self.sheath_voltage
        return self.compute_electron_collision_energy_loss(electron_temperature_ev) + self.compute_electron_ion_energy_loss(electron_temperature_ev, sheath_voltage)
           

    def compute_plasma_density(self, electron_temperature_ev: float | None = None, RF_power: float | None = None, 
                               sheath_voltage: float | None = None, chamber_radius_m: float | None = None, chamber_height_m: float | None = None) -> float:
        """Return plasma density from excitation and ionization energies."""
        if RF_power is None:
            RF_power = self.RF_power
        if sheath_voltage is None:
            sheath_voltage = self.sheath_voltage
        if chamber_radius_m is None:
            chamber_radius_m = self.chamber.chamber_radius_m
        if chamber_height_m is None:
            chamber_height_m = self.chamber.chamber_height_m
        return (
            (RF_power) / 
            (self.constants.electron_charge 
             * self.compute_bohm_velocity(electron_temperature_ev) 
             * self.compute_effective_area(chamber_radius_m, chamber_height_m) 
             * self.compute_total_energy_loss(electron_temperature_ev, sheath_voltage)) 
            
        )
