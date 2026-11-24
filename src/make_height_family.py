# Enumerate primitive integral short models in the target height shells.
# A model is included if H = max(4*abs(A)**3, 27*B**2) is in a shell
# [X, 2X), the discriminant is nonzero, and no prime q satisfies both
# q^4 | A and q^6 | B. No CM exclusion is applied.
# Save A, B, height, the Sage global minimal model, conductor, root number
# and CM status for each curve.

"""Independently enumerate the primitive height family, including CM curves."""
import argparse
import gzip
import math
import os
from pathlib import Path
import sys

from bvst_data import BASE, SCALES, check_family, encoded
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
    p.add_argument('--output-dir', '--output', type=Path, default=BASE/'work/reproduced/inputs',
                   help='directory for height_family.json.gz (default: work/reproduced/inputs/)')
    args = p.parse_args()
    rows = enumerate_family()
    save_outputs(args.output_dir, {'height_family.json.gz': gzip.compress(encoded(rows), mtime=0)})
    print('height family:', len(rows), 'curves; CM included', flush=True)
