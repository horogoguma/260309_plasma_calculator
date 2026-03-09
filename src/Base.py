"""기본 환경 설정과 공통 가져오기

이 모듈을 import 하면 pyspice가 필요로 하는 ngspice 경로 등이
자동으로 셋업된다. 다른 모듈에서는 단순히 ``import Base``
또는 ``from Base import initialize_pyspice`` 처럼 사용하면 된다.
"""

import os

# ngspice 설치 루트
NG_ROOT = r"C:\ngspice-31_64\Spice64"


def initialize_pyspice():
    """환경변수를 설정해 pyspice가 내부 ngspice DLL을 찾도록 한다."""
    # 프로세스 환경변수
    os.environ["PATH"] = NG_ROOT + r"\bin;" + os.environ.get("PATH", "")
    os.environ["SPICE_LIBRARY"] = NG_ROOT + r"\share\ngspice\scripts"

    # PySpice가 내부적으로 NGSPICE_PATH를 못 잡는 경우가 있어서,
    # 클래스 변수에 직접 넣어줌
    from PySpice.Spice.NgSpice.Shared import NgSpiceShared
    NgSpiceShared.NGSPICE_PATH = NG_ROOT

# 실행시 기본 초기화
initialize_pyspice()

#=================================================================================

#Top Matter

import numpy as np
import matplotlib.pyplot as plt
import sys

import PySpice
import PySpice.Logging.Logging as Logging
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Import bade tool


# Logger
logger = Logging.setup_logging()


# # create the circuit


# # add components to the circuit


# # run analysis # #


