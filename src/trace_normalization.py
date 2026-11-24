# 정규화된 shape A(t)/B와 비교할 tilt, translation 기준 곡선을 계산한다.
# Weighted trace는 z = w*a_p/(2*sqrt(p))이고 B = -2 ∫₀¹ A(t) dt다.
# Shape를 그릴 때는 부호를 포함한 B로 나눈다.
# 두 함수 모두 t 값이나 t 격자 배열을 받아 각 지점에서의 기준 곡선 값을 반환한다.
# 실험에 쓰는 0 <= t <= 1의 격자는 bvst_data.py의 grid()에서 만든다.
#
# make_figures.py의 shape()는 tilt를 그리고, 설정에 따라 translation도 함께 그린다.
# make_tables.py의 residual_quartiles()는 tilt를 사용해 A(t) - B*tilt(t)를 계산한다.
# 관측값 A, B가 어떻게 만들어지는지 보려면 arithmetic.py의 profile()을 읽으면 된다.

import numpy as np


def tilt_template(t):
    return -8/(3*np.pi)*np.maximum(1-np.asarray(t)**2, 0)**1.5


def translation_template(t):
    return -2/np.pi*np.sqrt(np.maximum(1-np.asarray(t)**2, 0))
