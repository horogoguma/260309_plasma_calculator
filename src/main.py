"""간단한 예제 스크립트

엑셀 파일에서 일부 매개변수를 읽어와서
스파이스 시뮬레이터와 플라즈마 계산기를 연동한다.
이 파일은 GUI가 붙기 전까지의 워크플로우 테스트용이다.
"""

from pathlib import Path
import pandas as pd

# local imports

# 루트 폴더를 파이썬 경로에 추가하면 모듈 import 문제를 피할 수 있다.
from pathlib import Path

# 패키지 이름을 포함한 절대 임포트
from src.spice import SpiceSimulator
from src.plasma import PlasmaCalculator

# pyspice 유닛을 쓰기 위해 import
from PySpice.Unit import *


def main():
    root = Path(__file__).resolve().parent.parent
    excel_path = root / "251209_Plasma_impedance_calculator_single frequency_900W_8Torr.xlsx"
    if not excel_path.exists():
        print(f"엑셀 파일을 찾을 수 없음: {excel_path}")
        return

    # 예시로 첫 시트의 첫 몇 열을 읽어본다
    df = pd.read_excel(excel_path, sheet_name=0)
    print("엑셀 데이터 (상위 5개 행):")
    print(df.head())

    # 정말 연결할 때는 필요한 셀을 골라서 파라미터로 넘긴다

    sim = SpiceSimulator()
    # 간단히 R=1k, C=1u 값을 넣어본다
    sim.build_rc_lowpass(1@u_kOhm, 1@u_uF)
    analysis = sim.run_ac(1@u_Hz, 1@u_MHz, points=20)

    # 예제로 node n2의 껍데기 값 중 첫번째를 사용
    voltage = float(analysis.n2[0])
    # PySpice에서는 전류를 바로 얻는 방법이 복잡하므로
    # 회로에서 R 값과 voltage 를 이용해 간단히 계산
    current = voltage / float(sim.R.resistance)
    power = voltage * current

    plasma = PlasmaCalculator()
    impedance = plasma.compute_impedance(voltage, current)
    print(f"계산된 임피던스: {impedance} Ω")
    print(f"계산된 전력: {power} W")


if __name__ == '__main__':
    main()
