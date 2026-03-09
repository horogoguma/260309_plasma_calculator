"""예제용 스크립트 - src 패키지의 클래스들을 사용해 간단한 계산을 보여줌"""

from pathlib import Path
import numpy as np

# paket import
from src.spice import SpiceSimulator
from src.plasma import PlasmaCalculator
from PySpice.Unit import *


def main():
    sim = SpiceSimulator()
    sim.build_rc_lowpass(1@u_kOhm, 1@u_uF)
    analysis = sim.run_ac(1@u_Hz, 1@u_MHz)

    voltage = float(analysis.n2[0])
    current = voltage / float(sim.R.resistance)
    power = voltage * current

    plasma = PlasmaCalculator()
    Z = plasma.compute_impedance(voltage, current)
    print(f"[예제] 임피던스: {Z} Ω, 전력: {power} W")


if __name__ == '__main__':
    main()
