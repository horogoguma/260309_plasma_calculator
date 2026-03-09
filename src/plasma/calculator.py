"""플라즈마 관련 이론적 계산을 담당하는 클래스

스파이스로부터 얻어온 전력/전류를 입력으로 받아
임피던스, 플로우, 기타 필요한 변수들을 계산한다.
"""

class PlasmaCalculator:
    def __init__(self, gas='argon', pressure_torr=8):
        self.gas = gas
        self.pressure_torr = pressure_torr

    def compute_impedance(self, voltage, current):
        """단순히 임피던스를 계산한다: Z = V / I"""
        if current == 0:
            raise ValueError("전류가 0입니다.")
        return voltage / current

    def compute_power_density(self, power, volume):
        """전력과 부피를 이용해 전력 밀도를 계산한다."""
        return power / volume

    # 여기서 복잡한 피드백 계산을 추가해 나갈 수 있다.
