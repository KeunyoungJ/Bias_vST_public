# Reproducing the elliptic curve numerical experiments

[Korean version](README.ko.md)

This repository accompanies the manuscript *Lower-order Bias in the Vertical Sato–Tate distribution and murmurations* by Keunyoung Jeong, Gyeongwon Oh, and Minseog Yang. Cite the manuscript and the repository commit used for your results.

<!-- FILES_BEGIN -->
<a id="file-map"></a>

## File inventory and roles

The package inventory lists **36 files**. Paths in the table are relative to the repository root.
Update this inventory and the input/output descriptions whenever files are added, removed, moved, or renamed.

```text
./
├── .gitattributes
├── .gitignore
├── README.ko.md
├── README.md
├── data/
│   ├── README.md
│   ├── conductor.npz
│   ├── conductor_family.json.gz
│   ├── height.npz
│   ├── height_family.json.gz
│   ├── sample_counts_conductor.csv
│   ├── sample_counts_height.csv
│   └── table1_residuals.csv
├── plots/
│   ├── 01_B_conductor_full_range.pdf
│   ├── 01_B_conductor_full_range.png
│   ├── 01_B_height_full_range.pdf
│   ├── 01_B_height_full_range.png
│   ├── 02_normalized_shape_X40000_full_range.pdf
│   ├── 02_normalized_shape_X40000_full_range.png
│   ├── 02_normalized_shape_Y40000_full_range.pdf
│   ├── 02_normalized_shape_Y40000_full_range.png
│   ├── 03_normalized_shape_X40000_height_unweighted_cm.pdf
│   ├── 03_normalized_shape_X40000_height_unweighted_cm.png
│   ├── 05_A_over_B0_all_common_reliable_X40000.pdf
│   ├── 05_A_over_B0_all_common_reliable_X40000.png
│   ├── B0_conductor_multiscale_full_range.pdf
│   └── B0_conductor_multiscale_full_range.png
├── requirements.txt
├── src/
│   ├── arithmetic.py
│   ├── bvst_data.py
│   ├── make_figures.py
│   ├── make_height_family.py
│   ├── make_tables.py
│   ├── recompute_data.py
│   ├── reproduction_io.py
│   └── trace_normalization.py
└── tests/
    └── test_bvst_data.py
```

| File path | Role |
| --- | --- |
| [.gitattributes](.gitattributes) | LF text files; binary handling for arrays and compressed files |
| [.gitignore](.gitignore) | Excludes temporary caches, locks, and SQLite journals |
| [README.ko.md](README.ko.md) | Korean README: file inventory, environment, execution order, and conventions |
| [README.md](README.md) | English README: file inventory, environment, execution order, and conventions |
| [data/README.md](data/README.md) | Conductor snapshot provenance and license |
| [data/conductor.npz](data/conductor.npz) | Full computation results: weighted/unweighted statistics, SE, pair counts, and masks |
| [data/conductor_family.json.gz](data/conductor_family.json.gz) | Frozen curve-family input |
| [data/height.npz](data/height.npz) | Full computation results: weighted/unweighted statistics, SE, pair counts, and masks |
| [data/height_family.json.gz](data/height_family.json.gz) | Frozen curve-family input |
| [data/sample_counts_conductor.csv](data/sample_counts_conductor.csv) | Curve and curve–prime pair counts by shell |
| [data/sample_counts_height.csv](data/sample_counts_height.csv) | Curve and curve–prime pair counts by shell |
| [data/table1_residuals.csv](data/table1_residuals.csv) | Residual quartiles over the common bins |
| [plots/01_B_conductor_full_range.pdf](plots/01_B_conductor_full_range.pdf) | Paper figure: vector PDF |
| [plots/01_B_conductor_full_range.png](plots/01_B_conductor_full_range.png) | Paper figure: 300 dpi PNG |
| [plots/01_B_height_full_range.pdf](plots/01_B_height_full_range.pdf) | Paper figure: vector PDF |
| [plots/01_B_height_full_range.png](plots/01_B_height_full_range.png) | Paper figure: 300 dpi PNG |
| [plots/02_normalized_shape_X40000_full_range.pdf](plots/02_normalized_shape_X40000_full_range.pdf) | Paper figure: vector PDF |
| [plots/02_normalized_shape_X40000_full_range.png](plots/02_normalized_shape_X40000_full_range.png) | Paper figure: 300 dpi PNG |
| [plots/02_normalized_shape_Y40000_full_range.pdf](plots/02_normalized_shape_Y40000_full_range.pdf) | Paper figure: vector PDF |
| [plots/02_normalized_shape_Y40000_full_range.png](plots/02_normalized_shape_Y40000_full_range.png) | Paper figure: 300 dpi PNG |
| [plots/03_normalized_shape_X40000_height_unweighted_cm.pdf](plots/03_normalized_shape_X40000_height_unweighted_cm.pdf) | Paper figure: vector PDF |
| [plots/03_normalized_shape_X40000_height_unweighted_cm.png](plots/03_normalized_shape_X40000_height_unweighted_cm.png) | Paper figure: 300 dpi PNG |
| [plots/05_A_over_B0_all_common_reliable_X40000.pdf](plots/05_A_over_B0_all_common_reliable_X40000.pdf) | Paper figure: vector PDF |
| [plots/05_A_over_B0_all_common_reliable_X40000.png](plots/05_A_over_B0_all_common_reliable_X40000.png) | Paper figure: 300 dpi PNG |
| [plots/B0_conductor_multiscale_full_range.pdf](plots/B0_conductor_multiscale_full_range.pdf) | Paper figure: vector PDF |
| [plots/B0_conductor_multiscale_full_range.png](plots/B0_conductor_multiscale_full_range.png) | Paper figure: 300 dpi PNG |
| [requirements.txt](requirements.txt) | Python dependency versions; install SageMath separately |
| [src/arithmetic.py](src/arithmetic.py) | Arithmetic computation, curve-level SE, and SQLite-based resumption |
| [src/bvst_data.py](src/bvst_data.py) | Conventions, input/result loaders, validation, and README inventory updates |
| [src/make_figures.py](src/make_figures.py) | Generates seven paper figures from the full computation results |
| [src/make_height_family.py](src/make_height_family.py) | Independent enumeration of all primitive short models |
| [src/make_tables.py](src/make_tables.py) | Generates sample counts, pair counts, and Table 1 as CSV files |
| [src/recompute_data.py](src/recompute_data.py) | Entry point for independent conductor and height computations |
| [src/reproduction_io.py](src/reproduction_io.py) | Preserves different existing outputs and reuses identical outputs |
| [src/trace_normalization.py](src/trace_normalization.py) | Tilt/translation templates and trace conventions |
| [tests/test_bvst_data.py](tests/test_bvst_data.py) | Reproduction code regression tests |

<!-- FILES_END -->

## Scope and conventions

The entire family is processed in a single loop. Weighted and unweighted statistics use the same $a_p$ values.
The conductor and primitive-height shells are $[X,2X)$ for $X=5000,10000,20000,40000$.
For primitive integral short models, the height is $H(E)=\max(4|A|^3,27B^2)$.
For both orderings, the prime variable is $v=p/N(E)$; only good primes with $p\ge5$ and $p\nmid N(E)$ are used.
The prime bins are $J_j=[(j+2)/100,(j+3)/100)$, $j=0,\ldots,97$, with bin membership determined by integer comparisons.
The weighted trace is $z=w(E)a_p(E)/(2\sqrt p)$. For each curve, $\sqrt p\,g_t(z)$ and $w(E)a_p(E)$
are summed within each bin to obtain the contributions to $\mathcal A$ and $B$, respectively.
Averages use the total number of curves, including curves with no primes in a bin.
Unweighted statistics omit the root number. Shapes are divided by signed $B$, and relative residuals by $|B|$.
SE denotes the analytic standard error at the curve level, accounting for curve multiplicities within isogeny classes. No new bootstrap was performed.

## Quick reproduction from the bundled results

Run these commands from the repository root using Python 3.11 or 3.12. This procedure uses the bundled NPZ files and the Python dependencies in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/bvst_data.py
python -m unittest discover -s tests
python src/make_figures.py
python src/make_tables.py
```

Validation requires both curve-family inputs and both NPZ files. To check only one family, use `--family conductor` or `--family height`. Generated figures and tables go to `work/reproduced/plots/` and `work/reproduced/tables/`; the bundled files are unchanged.

## Independent arithmetic recomputation

The reference full run used SageMath 10.6, Python 3.12.11, and NumPy 2.3.2 on WSL/Linux. Use `sage -python` for arithmetic and the virtual environment above for the figures and tables. Run the small examples first to check both curve families.

```bash
sage -python src/recompute_data.py --family conductor --scope smoke --workers 2
sage -python src/recompute_data.py --family height --scope smoke --workers 2
```

To check resumption, append `--max-batches 1` to the first invocation for a family, then repeat the original command to finish. Start each family with a fresh checkpoint directory for this check.

The full rerun uses the frozen inputs in `data/`.

```bash
sage -python src/recompute_data.py --family conductor --scope full --workers 4
sage -python src/recompute_data.py --family height --scope full --workers 4
python src/bvst_data.py --data-dir work/reproduced/data
python src/make_figures.py --data-dir work/reproduced/data --output-dir work/recomputed/plots
python src/make_tables.py --data-dir work/reproduced/data --output-dir work/recomputed/tables
```

Full runs compute coefficients and root numbers from the frozen curve lists, not from the bundled NPZ files. No access to the original repository, external database, or existing coefficient cache is required. The conductor snapshot is an input, not generated by these scripts. To regenerate the height input on its own, use `sage -python src/make_height_family.py` (default destination: `work/reproduced/inputs/`); to use that snapshot for a new height run, pass `--family-dir work/reproduced/inputs` and a fresh `--work-dir`.

The default full result directory is `work/reproduced/data/` (`--output-dir` changes it). Checkpoints live separately in `work/{scope}_{family}/` (`--work-dir` changes it). The SQLite database, `progress.json`, and `run.json` record committed batches; repeat the same command to resume. Source and input hashes are part of the checkpoint identity. After an input or source change, use a fresh checkpoint directory and a fresh output directory. Use separate output directories to compare regenerated plots or tables against earlier files: existing outputs with different bytes are not overwritten.

`--max-seconds 0` removes the time limit. The default storage limit is 10 GiB; repeat `--budget-root` to apply it to the combined usage of the specified paths. Ctrl-C or SIGTERM pauses at a committed batch boundary; an in-flight batch may take time to finish.


## Input and output locations

- `data/conductor_family.json.gz`: a frozen LMFDB snapshot with 329998 isogeny-class representatives and multiplicities for a total of 496582 curves. See the [data README](data/README.md) for provenance and CC BY-SA 4.0 licensing.
- `data/height_family.json.gz`: 5422 primitive models independently enumerated by the bundled code.
- `data/conductor.npz`, `data/height.npz`: full computation results, containing weighted/unweighted statistics, SE, normalizers, pair counts, masks, and metadata.
- `data/sample_counts_conductor.csv`, `data/sample_counts_height.csv`, `data/table1_residuals.csv`: three tables computed from the results.
- `plots/`: seven paper figures in PNG and PDF formats. Existing manuscript filenames are retained. Figure 1(a) and Figure 3 use the same file.

Input-family hashes, code hashes, environment details, and normalization are recorded in the SQLite identity and the NPZ `metadata_json` field.
Different existing result files are not overwritten automatically. Detailed internal execution histories and validation artifacts for earlier conventions are preserved outside the public package.

| Manuscript figure | Filename in `plots/` (a PDF with the same stem is also provided) |
| --- | --- |
| Figure 1(a), Figure 3 | `02_normalized_shape_Y40000_full_range.png` |
| Figure 1(b) | `02_normalized_shape_X40000_full_range.png` |
| Figure 1(c) | `05_A_over_B0_all_common_reliable_X40000.png` |
| Figure 1(d) | `03_normalized_shape_X40000_height_unweighted_cm.png` |
| Figure 2 | `01_B_conductor_full_range.png` |
| Figure 4(a) | `01_B_height_full_range.png` |
| Figure 4(b) | `B0_conductor_multiscale_full_range.png` |

The conductor-shape filename retains `Y40000` for compatibility with the existing TeX source; the scale inside the figure is labeled $X$.
The four normalized-shape plots share title, axis, legend, and colorbar formats, with subscripts distinguishing ordering and weighting.

## Bin selection and tables

Weighted shapes use a discovery condition requiring $|B|>2\mathrm{SE}(B)$ in at least two of the first three shells, together with the same condition in the final shell.
Unweighted shapes use the common bins passing both weighted and unweighted amplitude conditions in the final shell, without an additional discovery condition.
At $X=40000$, the weighted conductor/height plots contain 96/61 bins, and the unweighted conductor/height plots contain 90/17 bins.
The 17 unweighted height bins and the 61 displayed weighted height bins have an intersection of 13 bins.
Amplitude plots use all 98 bins before selection. Sample and pair counts also use the full totals before selection.
Table 1 uses the common set in the final conductor shell, the trapezoidal approximation to the $L^2(0,1)$ norm on a 301-point $t$ grid, and linear-interpolated quartiles across bins.
Since the unweighted height plot uses a different common set from the displayed weighted set, the number of displayed bins alone does not directly compare noise levels.

## Full computation and validation completed on 2026-11-03

The public code recomputed all coefficients for 329998 conductor representatives and 5422 height models.
With four workers, the arithmetic computations took approximately 2 hours 39 minutes for conductor and 22 minutes for height.
Curve counts, curve–prime pair counts, grids, and selection masks agree exactly with the internal reference computations.
The maximum absolute difference is below $1.23\times10^{-13}$ for means and below $2\times10^{-15}$ for analytic SE.
All 12 entries of Table 1 agree to six decimal places. Resuming the completed computations produced zero new coefficients or batches and byte-identical NPZ files.

Small-scale validation included 114 direct point counts, 16 direct profile checks, boundary checks, multiplicities, means/SE, actual interruption/resumption, and tamper detection.
Both families also passed arithmetic computation in an isolated copy with access to the original repository data and network reads blocked.
These November 3 checks used the WSL/Linux reference environment.

## Clean-checkout verification on 2026-11-24

On macOS, a fresh Python 3.11.5 virtual environment with NumPy 2.3.2 and Matplotlib 3.10.5 passed the data check and all three regression tests. All three regenerated CSV files matched the bundled files byte for byte. The seven figures regenerated in both PNG and PDF and matched the original renderer byte for byte when run in the same Mac environment. Rendering bytes can vary between this environment and the WSL/Linux reference.

Smoke runs with SageMath 10.4 and NumPy 1.26.3 processed 24 records per family using two workers. Both resumed after a one-batch pause. Repeating each completed run added zero coefficients and batches and produced the same NPZ bytes.
