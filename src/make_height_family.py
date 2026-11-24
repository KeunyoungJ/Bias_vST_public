# public_release/에서 Sage 환경의 Python으로 height 곡선 목록을 생성한다.
#   python src/make_height_family.py
# --output은 height_family.json.gz를 저장할 폴더다. 기본은 public_release/data/다.
#
# enumerate_family()는 높이 H = max(4*abs(A)**3, 27*B**2)의 상한으로
# 정수 short model y^2 = x^3 + A*x + B의 계수 A, B 범위를 정한다.
# 곡선은 H가 목표 shell [X, 2X)에 속하고 판별식이 0이 아니며 primitive일 때 포함된다.
# primitive()는 어떤 소수 q에 대해 q^4 | A와 q^6 | B가 동시에 성립하는지 검사한다.
#
# 각 레코드에 원래 계수 A, B와 높이, Sage의 global minimal model 계수,
# conductor, root number, CM 여부를 함께 기록한다.
# 이 파일을 입력으로 쓰는 다음 단계는 recompute_data.py --family height다.
# 곡선 목록을 읽고 검사하는 함수는 bvst_data.py의 load_family()와 check_family()다.

"""Primitive integral short model을 CM 제외 없이 유한 box에서 독립 열거한다."""
import argparse
import gzip
import math
import os
from pathlib import Path
import sys

from bvst_data import BASE, SCALES, check_family, encoded, refresh_readme
from reproduction_io import save_outputs


def primitive(a, b):
    g = math.gcd(abs(a), abs(b))
    q = 2
    while q*q <= g:
        if g % q == 0:
            if a % q**4 == 0 and b % q**6 == 0:
                return False
            while g % q == 0: g //= q
        q += 1
    return not (g > 1 and a % g**4 == 0 and b % g**6 == 0)


def enumerate_family(scales=SCALES):
    os.environ.setdefault('DOT_SAGE', '/tmp/bvst-public-cm-sage')
    os.environ['PATH'] = str(Path(sys.executable).resolve().parent)+os.pathsep+os.environ.get('PATH', '')
    from sage.all import EllipticCurve, QQ
    maximum = 2*max(scales)
    amax = 0
    while 4*(amax+1)**3 < maximum: amax += 1
    bmax = math.isqrt((maximum-1)//27)
    rows = []
    for a in range(-amax, amax+1):
        for b in range(-bmax, bmax+1):
            h = max(4*abs(a)**3, 27*b*b)
            x = next((x for x in scales if x <= h < 2*x), None)
            if x is None or 4*a**3+27*b*b == 0 or not primitive(a, b):
                continue
            e = EllipticCurve(QQ, [a, b]).global_minimal_model()
            rows.append({'scale': x, 'primitive_AB': [a, b], 'height': h,
                         'ainvs': list(map(int, e.a_invariants())),
                         'conductor': int(e.conductor()), 'root_number': int(e.root_number()),
                         'is_cm': bool(e.has_cm())})
    rows.sort(key=lambda r: (r['scale'], r['conductor'], r['ainvs']))
    assert len({tuple(r['ainvs']) for r in rows}) == len(rows)
    check_family('height', rows)
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=BASE/'data')
    args = p.parse_args()
    rows = enumerate_family()
    save_outputs(args.output, {'height_family.json.gz': gzip.compress(encoded(rows), mtime=0)})
    refresh_readme()
    print('height family:', len(rows), 'curves; CM included', flush=True)
