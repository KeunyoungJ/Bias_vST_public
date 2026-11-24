"""Regenerate the sample-count tables and Table 1 from aggregate NPZ files."""

# Sample counts give the number of curves and curve-prime pairs per shell.
# Table 1 uses the common reliable bins of the final conductor shell. It
# records quartiles across bins of the L2 residual A(t) - B*tilt(t), computed
# by trapezoidal integration, and of the residual normalized by |B|.

import argparse
import csv
from pathlib import Path
from io import StringIO
import numpy as np
from bvst_data import BASE, load_profiles, verify
from reproduction_io import artifact_arguments, save_outputs
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


def main(root=BASE, *, data_dir=None, family_dir=None, output_dir=None, kinds=('conductor', 'height')):
    root = Path(root)
    if output_dir is None:
        output_dir = root/'work/reproduced/tables'
    verify(root, data_dir=data_dir, family_dir=family_dir, kinds=kinds)
    outputs = {}
    for kind in kinds:
        d = load_profiles(kind, root, data_dir=data_dir)
        rows = [(int(x), int(d['curves'][i]), int(d['prime_curve_pairs'][i].sum())) for i, x in enumerate(d['scales'])]
        outputs[f'sample_counts_{kind}.csv'] = csv_bytes(['X', 'curves', 'pairs'], rows)
        if kind == 'conductor':
            outputs['table1_residuals.csv'] = csv_bytes(['weighting', 'norm', 'Q1', 'median', 'Q3'], residual_quartiles(d))
    if not outputs: raise ValueError('Compute conductor or height first')
    save_outputs(output_dir, outputs)
    print('tables:', len(outputs), 'CSV files in', output_dir, flush=True)


if __name__ == '__main__':
    args = artifact_arguments(argparse.ArgumentParser(description=__doc__), 'tables')
    main(**args)
