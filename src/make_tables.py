# public_release/에서 python src/make_tables.py를 실행하면 집계 NPZ로 표를 만든다.
# main()은 bvst_data.py에서 data/conductor.npz와 data/height.npz를 읽고,
# 존재하는 family별로 sample_counts_{family}.csv를 data/에 저장한다.
# 각 행은 한 shell의 곡선 수와 전체 bin에 걸친 curve–prime pair 수를 담는다.
#
# Conductor의 Table 1은 residual_quartiles()에서 계산한다. 마지막 shell(X=40000)의
# common_reliable_bins에 대해 weighted와 unweighted 각각 A(t) - B*tilt(t)를 구한다.
# 잔차의 L2 크기를 t 격자에서 사다리꼴 공식으로 계산하고, 이를 |B|로 나눈 값도 구한다.
# 각 값의 bin 방향 사분위수를 data/table1_residuals.csv에 기록한다.
#
# tilt 공식은 trace_normalization.py, CSV 저장 규칙은 reproduction_io.py에 있다.

import csv
from io import StringIO
import numpy as np
from bvst_data import BASE, load_profiles, refresh_readme, verify
from reproduction_io import save_outputs
from trace_normalization import tilt_template


def csv_bytes(header, rows):
    f = StringIO()
    w = csv.writer(f, lineterminator='\n')
    w.writerow(header); w.writerows(rows)
    return f.getvalue().encode()


def residual_quartiles(d):
    mask = d['common_reliable_bins'][-1]
    rows = []
    for mode in ('weighted', 'unweighted'):
        a, b = d['A_'+mode][-1, mask], d['B_'+mode][-1, mask]
        raw = np.sqrt(np.trapezoid((a-b[:, None]*tilt_template(d['t_grid']))**2, d['t_grid'], axis=-1))
        for metric, values in [('raw', raw), ('relative', raw/abs(b))]:
            rows.append((mode, metric, *map(float, np.quantile(values, [.25, .5, .75], method='linear'))))
    return sorted(rows, key=lambda row: (row[1] == 'relative', row[0] == 'unweighted'))


def main(root=BASE):
    verify(root)
    outputs = {}
    for kind in ('conductor', 'height'):
        if not (root/f'data/{kind}.npz').exists(): continue
        d = load_profiles(kind, root)
        rows = [(int(x), int(d['curves'][i]), int(d['prime_curve_pairs'][i].sum())) for i, x in enumerate(d['scales'])]
        outputs[f'sample_counts_{kind}.csv'] = csv_bytes(['X', 'curves', 'pairs'], rows)
        if kind == 'conductor':
            outputs['table1_residuals.csv'] = csv_bytes(['weighting', 'norm', 'Q1', 'median', 'Q3'], residual_quartiles(d))
    if not outputs: raise ValueError('Compute conductor or height first')
    save_outputs(root/'data', outputs)
    refresh_readme(root)
    print('tables:', len(outputs), 'CSV files', flush=True)


if __name__ == '__main__':
    main()
