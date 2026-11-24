# Reproducing the elliptic curve numerical experiments

[Korean version](README.md)

<!-- FILES_BEGIN -->
<a id="file-map"></a>

## File inventory and roles

The package currently contains **34 files**, including both READMEs. Paths in the table are relative to the repository root.
Update this inventory and the input/output descriptions whenever files are added, removed, moved, or renamed.

```text
public_release/
├── .gitattributes
├── .gitignore
├── README.en.md
├── README.md
├── data/
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
└── src/
    ├── arithmetic.py
    ├── bvst_data.py
    ├── make_figures.py
    ├── make_height_family.py
    ├── make_tables.py
    ├── recompute_data.py
    ├── reproduction_io.py
    └── trace_normalization.py
```

| File path | Role |
| --- | --- |
| [public_release/.gitattributes](.gitattributes) | LF text files; binary handling for arrays and compressed files |
| [public_release/.gitignore](.gitignore) | Excludes temporary caches, locks, and SQLite journals |
| [public_release/README.en.md](README.en.md) | English README: file inventory, environment, execution order, and conventions |
| [public_release/README.md](README.md) | Korean README: file inventory, environment, execution order, and conventions |
| [public_release/data/conductor.npz](data/conductor.npz) | Full computation results: weighted/unweighted statistics, SE, pair counts, and masks |
| [public_release/data/conductor_family.json.gz](data/conductor_family.json.gz) | Frozen curve-family input |
| [public_release/data/height.npz](data/height.npz) | Full computation results: weighted/unweighted statistics, SE, pair counts, and masks |
| [public_release/data/height_family.json.gz](data/height_family.json.gz) | Frozen curve-family input |
| [public_release/data/sample_counts_conductor.csv](data/sample_counts_conductor.csv) | Curve and curve–prime pair counts by shell |
| [public_release/data/sample_counts_height.csv](data/sample_counts_height.csv) | Curve and curve–prime pair counts by shell |
| [public_release/data/table1_residuals.csv](data/table1_residuals.csv) | Residual quartiles over the common bins |
| [public_release/plots/01_B_conductor_full_range.pdf](plots/01_B_conductor_full_range.pdf) | Paper figure: vector PDF |
| [public_release/plots/01_B_conductor_full_range.png](plots/01_B_conductor_full_range.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/01_B_height_full_range.pdf](plots/01_B_height_full_range.pdf) | Paper figure: vector PDF |
| [public_release/plots/01_B_height_full_range.png](plots/01_B_height_full_range.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/02_normalized_shape_X40000_full_range.pdf](plots/02_normalized_shape_X40000_full_range.pdf) | Paper figure: vector PDF |
| [public_release/plots/02_normalized_shape_X40000_full_range.png](plots/02_normalized_shape_X40000_full_range.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/02_normalized_shape_Y40000_full_range.pdf](plots/02_normalized_shape_Y40000_full_range.pdf) | Paper figure: vector PDF |
| [public_release/plots/02_normalized_shape_Y40000_full_range.png](plots/02_normalized_shape_Y40000_full_range.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/03_normalized_shape_X40000_height_unweighted_cm.pdf](plots/03_normalized_shape_X40000_height_unweighted_cm.pdf) | Paper figure: vector PDF |
| [public_release/plots/03_normalized_shape_X40000_height_unweighted_cm.png](plots/03_normalized_shape_X40000_height_unweighted_cm.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/05_A_over_B0_all_common_reliable_X40000.pdf](plots/05_A_over_B0_all_common_reliable_X40000.pdf) | Paper figure: vector PDF |
| [public_release/plots/05_A_over_B0_all_common_reliable_X40000.png](plots/05_A_over_B0_all_common_reliable_X40000.png) | Paper figure: 300 dpi PNG |
| [public_release/plots/B0_conductor_multiscale_full_range.pdf](plots/B0_conductor_multiscale_full_range.pdf) | Paper figure: vector PDF |
| [public_release/plots/B0_conductor_multiscale_full_range.png](plots/B0_conductor_multiscale_full_range.png) | Paper figure: 300 dpi PNG |
| [public_release/requirements.txt](requirements.txt) | Python dependency versions; install SageMath separately |
| [public_release/src/arithmetic.py](src/arithmetic.py) | Arithmetic computation, curve-level SE, and SQLite-based resumption |
| [public_release/src/bvst_data.py](src/bvst_data.py) | Conventions, input/result loaders, validation, and README inventory updates |
| [public_release/src/make_figures.py](src/make_figures.py) | Generates seven paper figures from the full computation results |
| [public_release/src/make_height_family.py](src/make_height_family.py) | Independent enumeration of all primitive short models |
| [public_release/src/make_tables.py](src/make_tables.py) | Generates sample counts, pair counts, and Table 1 as CSV files |
| [public_release/src/recompute_data.py](src/recompute_data.py) | Entry point for independent conductor and height computations |
| [public_release/src/reproduction_io.py](src/reproduction_io.py) | Preserves different existing outputs and reuses identical outputs |
| [public_release/src/trace_normalization.py](src/trace_normalization.py) | Tilt/translation templates and trace conventions |

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

## Environment and execution order

Verified environment: Python 3.12.11, SageMath 10.6, NumPy 2.3.2, Matplotlib 3.10.5, WSL/Linux.
`requirements.txt` specifies Python package versions; install SageMath separately. Run the commands using Sage's Python environment.
Execute the following commands inside `public_release/`. No access to the original repository, its coefficient caches, or an external database is required.
The frozen conductor-family input in `data/conductor_family.json.gz` must be present; the Python scripts alone do not supply that snapshot.

```bash
python src/make_height_family.py
python src/bvst_data.py
python src/recompute_data.py --family conductor --scope full --workers 4
python src/recompute_data.py --family height --scope full --workers 4
python src/make_figures.py
python src/make_tables.py
```

`make_height_family.py` generates the height-family input, and `bvst_data.py` validates the bundled inputs and results.
`recompute_data.py` computes the numerical data for each family; `make_figures.py` generates the plots, and `make_tables.py` generates the CSV tables.
To regenerate only the figures and tables from the bundled NPZ results, run the final two commands.

`--scope full` recomputes coefficients and root numbers for the entire family rather than copying existing aggregate results.
Use `--work-dir` to choose the location of the coefficient/resumption SQLite database; the default is `work/{scope}_{family}/`.
The preserved SQLite database, `progress.json`, and `run.json` are computation and resumption records, rather than disposable caches.
Repeating the same command resumes after the last committed batch. Resuming a completed computation produces no new coefficients.
`--max-seconds 0` removes the time limit; the default `--max-bytes` limit is 10 GiB.
Repeat `--budget-root` to apply the storage budget to the combined usage of the specified paths. Coefficients and moments are committed in the same transaction.
Check storage requirements before a long computation. SIGTERM/Ctrl-C stops execution at a committed batch boundary.
Conductor and height computations use separate checkpoint identities, so running one family does not trigger recomputation of the other.
The inventory at the top is updated when files are generated. After generating figures and tables, consult it for all output locations.

## Input and output locations

- `data/conductor_family.json.gz`: a frozen LMFDB snapshot with 329998 isogeny-class representatives and multiplicities for a total of 496582 curves.
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

Weighted shapes use a discovery condition requiring $|B|>2\operatorname{SE}(B)$ in at least two of the first three shells, together with the same condition in the final shell.
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
This verifies independent execution in the existing Sage environment; dependency installation on a fresh operating system has not been verified.
The previous public preparation package was moved to an internal archive and its restoration verified by hashes. The package has not yet been published remotely.

## Internal coefficient databases excluded from Git

The two coefficient databases from the full computations are preserved locally outside the public folder and are not included in Git.
They are outside the 34-file public-package inventory above.

- `results/current/elliptic_curves/public_cm_20261103-002218/checkpoint/conductor/coefficients.sqlite`: approximately 2.54 GiB.
- `results/current/elliptic_curves/public_cm_20261103-002218/checkpoint/height/coefficients.sqlite`: approximately 301.06 MiB.

These paths are relative to the repository root. In a new clone, regenerate the databases using the `--scope full` commands above.
The bundled NPZ files suffice for generating figures and tables. Reusing an existing database requires a separately preserved copy.
