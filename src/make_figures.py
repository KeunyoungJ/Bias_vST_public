# public_release/에서 python src/make_figures.py를 실행하면 집계 NPZ로 그림을 만든다.
# main()은 bvst_data.py의 verify()를 먼저 호출하고, build_figures()는
# data/conductor.npz와 data/height.npz 중 존재하는 파일에서 그릴 패널을 정한다.
#
# amplitude()는 네 shell의 B를 bin 중점 v_J에 대해 그린다.
# shape()는 마지막 shell(X=40000)에서 선택된 bin마다 A(t)/B를 그린다.
# Weighted 그림에는 eligible, unweighted 그림에는 common_reliable_bins를 쓴다.
# 비교 곡선인 tilt와 translation의 공식은 trace_normalization.py에 있다.
#
# 두 family의 NPZ가 있으면 그림 일곱 장을 각각 PNG와 PDF로 plots/에 저장한다.
# 그림 파일명은 기존 원고의 참조에 맞춘다.
# 어떤 집계 배열이 어느 그림에 들어가는지 보려면 build_figures()부터 읽으면 된다.
# 저장 단계는 reproduction_io.py의 save_outputs()를 사용한다.

import os
from io import BytesIO
from bvst_data import BASE, load_profiles, refresh_readme, verify
from reproduction_io import save_outputs
from trace_normalization import tilt_template, translation_template

os.environ.setdefault('MPLCONFIGDIR', '/tmp/bvst-public-cm-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.ticker import FormatStrFormatter
import numpy as np

COLORS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7']


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.labelsize': 16,
        'axes.titlesize': 14, 'legend.fontsize': 11, 'legend.frameon': False,
        'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42, 'ps.fonttype': 42})


def amplitude(d, values, letter):
    fig, ax = plt.subplots(figsize=(9.5, 6.2), layout='constrained')
    for i, x in enumerate(d['scales']):
        ax.plot(d['v_midpoints'], values[i], color=COLORS[i], lw=1.8, label=rf'$X={int(x):,}$')
    ax.axhline(0, color='.35', lw=.8)
    ax.set(xlim=(0, 1), xlabel=r'$v_J$', ylabel=rf'$B^{letter}_{{2,X}}(J)$')
    ax.set_xticks(np.linspace(0, 1, 6)); ax.grid(axis='y', alpha=.18, lw=.6)
    ax.legend(ncols=4, loc='lower left', columnspacing=1.4, handlelength=2.2)
    return fig


def shape(d, mode, mask, letter, translation):
    indices = np.flatnonzero(mask)
    a, b = d['A_'+mode][-1], d['B_'+mode][-1]
    fig, ax = plt.subplots(figsize=(9.5, 6.2), layout='constrained')
    norm, cmap = Normalize(.02, 1), plt.get_cmap('viridis')
    for j in indices:
        ax.plot(d['t_grid'], a[j]/b[j], color=cmap(norm(d['v_midpoints'][j])), alpha=.72, lw=1.05)
    ax.plot(d['t_grid'], tilt_template(d['t_grid']), 'k-', lw=2.5, label=r'$\Psi_{\mathrm{tilt}}$')
    if translation:
        ax.plot(d['t_grid'], translation_template(d['t_grid']), 'k--', lw=2, label=r'$\Psi_{\mathrm{tr}}$')
    ax.set(xlim=(0, 1), xlabel=r'$t$', ylabel=rf'$\mathcal{{A}}^{letter}_{{2,X,J}}(t)/B^{letter}_{{2,X}}(J)$',
           title=rf'$X=40\,000$ ({len(indices)} selected bins)')
    ax.grid(alpha=.18, lw=.6); ax.legend(loc='lower right')
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                     ticks=[.02, .2, .4, .6, .8, 1.], pad=.025)
    cb.set_label(r'$v_J$'); cb.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    for line, j in zip(ax.lines, indices):
        np.testing.assert_array_equal(line.get_ydata(), a[j]/b[j])
    return fig


def build_figures(root=BASE):
    style()
    figures = {}
    if (root/'data/conductor.npz').exists():
        d = load_profiles('conductor', root)
        figures.update({
            '01_B_conductor_full_range': amplitude(d, d['B_weighted'], 'N'),
            '02_normalized_shape_Y40000_full_range': shape(d, 'weighted', d['eligible'][-1], 'N', True),
            '05_A_over_B0_all_common_reliable_X40000': shape(d, 'unweighted', d['common_reliable_bins'][-1], '{0}', False),
            'B0_conductor_multiscale_full_range': amplitude(d, d['B_unweighted'], '{0}')})
    if (root/'data/height.npz').exists():
        d = load_profiles('height', root)
        figures.update({
            '01_B_height_full_range': amplitude(d, d['B_weighted'], 'H'),
            '02_normalized_shape_X40000_full_range': shape(d, 'weighted', d['eligible'][-1], 'H', True),
            '03_normalized_shape_X40000_height_unweighted_cm': shape(d, 'unweighted', d['common_reliable_bins'][-1], '{H,0}', False)})
    if not figures: raise ValueError('Compute conductor or height data first')
    return figures


def main(root=BASE):
    verify(root)
    figures = build_figures(root)
    try:
        outputs = {}
        for stem, fig in figures.items():
            for ext in ('png', 'pdf'):
                f = BytesIO()
                metadata = {'CreationDate': None, 'ModDate': None} if ext == 'pdf' else {}
                fig.savefig(f, format=ext, dpi=300, metadata=metadata)
                outputs[f'{stem}.{ext}'] = f.getvalue()
        save_outputs(root/'plots', outputs)
        refresh_readme(root)
        print('figures:', len(figures), 'PNG/PDF files:', len(outputs), flush=True)
    finally:
        for fig in figures.values(): plt.close(fig)


if __name__ == '__main__':
    main()
