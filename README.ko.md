# 타원곡선 수치 실험 재현

[English version](README.md)

이 저장소는 Keunyoung Jeong, Gyeongwon Oh, Minseog Yang의 원고 *Lower-order Bias in the Vertical Sato–Tate distribution and murmurations*의 수치 실험을 재현한다. 결과를 인용할 때 원고와 실행에 사용한 저장소 커밋을 함께 표기한다.

<!-- FILES_BEGIN -->
<a id="file-map"></a>

## 현재 파일 위치와 역할

현재 파일 목록에는 **36개**의 파일이 있다. 표의 경로는 저장소 루트 기준이다.
파일을 추가·삭제·이동·이름 변경할 때 이 목록과 입출력 설명을 함께 갱신한다.

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

| 파일 경로 | 역할 |
| --- | --- |
| [.gitattributes](.gitattributes) | 텍스트 LF·배열 및 압축 파일의 binary 처리 |
| [.gitignore](.gitignore) | 임시 cache·lock·SQLite journal 제외 |
| [README.ko.md](README.ko.md) | 한국어판: 파일 목록·환경·실행 순서·규약 |
| [README.md](README.md) | 영어판: 파일 목록·환경·실행 순서·규약 |
| [data/README.md](data/README.md) | Conductor 스냅샷 출처와 라이선스 |
| [data/conductor.npz](data/conductor.npz) | 새 전체 계산의 weighted/unweighted·SE·pair 수·mask |
| [data/conductor_family.json.gz](data/conductor_family.json.gz) | 고정 곡선 목록 입력 |
| [data/height.npz](data/height.npz) | 새 전체 계산의 weighted/unweighted·SE·pair 수·mask |
| [data/height_family.json.gz](data/height_family.json.gz) | 고정 곡선 목록 입력 |
| [data/sample_counts_conductor.csv](data/sample_counts_conductor.csv) | shell별 curve 수·curve–prime pair 수 |
| [data/sample_counts_height.csv](data/sample_counts_height.csv) | shell별 curve 수·curve–prime pair 수 |
| [data/table1_residuals.csv](data/table1_residuals.csv) | common bin에서 계산한 잔차 사분위수 |
| [plots/01_B_conductor_full_range.pdf](plots/01_B_conductor_full_range.pdf) | 논문 그림: vector PDF |
| [plots/01_B_conductor_full_range.png](plots/01_B_conductor_full_range.png) | 논문 그림: 300 dpi PNG |
| [plots/01_B_height_full_range.pdf](plots/01_B_height_full_range.pdf) | 논문 그림: vector PDF |
| [plots/01_B_height_full_range.png](plots/01_B_height_full_range.png) | 논문 그림: 300 dpi PNG |
| [plots/02_normalized_shape_X40000_full_range.pdf](plots/02_normalized_shape_X40000_full_range.pdf) | 논문 그림: vector PDF |
| [plots/02_normalized_shape_X40000_full_range.png](plots/02_normalized_shape_X40000_full_range.png) | 논문 그림: 300 dpi PNG |
| [plots/02_normalized_shape_Y40000_full_range.pdf](plots/02_normalized_shape_Y40000_full_range.pdf) | 논문 그림: vector PDF |
| [plots/02_normalized_shape_Y40000_full_range.png](plots/02_normalized_shape_Y40000_full_range.png) | 논문 그림: 300 dpi PNG |
| [plots/03_normalized_shape_X40000_height_unweighted_cm.pdf](plots/03_normalized_shape_X40000_height_unweighted_cm.pdf) | 논문 그림: vector PDF |
| [plots/03_normalized_shape_X40000_height_unweighted_cm.png](plots/03_normalized_shape_X40000_height_unweighted_cm.png) | 논문 그림: 300 dpi PNG |
| [plots/05_A_over_B0_all_common_reliable_X40000.pdf](plots/05_A_over_B0_all_common_reliable_X40000.pdf) | 논문 그림: vector PDF |
| [plots/05_A_over_B0_all_common_reliable_X40000.png](plots/05_A_over_B0_all_common_reliable_X40000.png) | 논문 그림: 300 dpi PNG |
| [plots/B0_conductor_multiscale_full_range.pdf](plots/B0_conductor_multiscale_full_range.pdf) | 논문 그림: vector PDF |
| [plots/B0_conductor_multiscale_full_range.png](plots/B0_conductor_multiscale_full_range.png) | 논문 그림: 300 dpi PNG |
| [requirements.txt](requirements.txt) | Python 의존성 버전; SageMath는 별도 설치 |
| [src/arithmetic.py](src/arithmetic.py) | 동일 loop의 원계산·curve SE·SQLite 재개 |
| [src/bvst_data.py](src/bvst_data.py) | 명시적 규약·입력/결과 loader·검사·이 파일 목록 갱신 |
| [src/make_figures.py](src/make_figures.py) | 새 전체 계산 자료에서 일곱 논문 그림 생성 |
| [src/make_height_family.py](src/make_height_family.py) | primitive short model 전체 독립 열거 |
| [src/make_tables.py](src/make_tables.py) | 표본 수·pair 수·Table 1 CSV 생성 |
| [src/recompute_data.py](src/recompute_data.py) | conductor/height를 독립 실행하는 원계산 진입점 |
| [src/reproduction_io.py](src/reproduction_io.py) | 다른 기존 출력 보존·동일 출력 재사용 |
| [src/trace_normalization.py](src/trace_normalization.py) | tilt/translation template와 trace 규약 |
| [tests/test_bvst_data.py](tests/test_bvst_data.py) | 재현 코드 회귀 테스트 |

<!-- FILES_END -->

## 계산 범위와 규약

전체 family를 하나의 loop에서 계산한다. Weighted/unweighted는 같은 $a_p$를 사용한다.
Conductor 또는 primitive height의 shell은 $[X,2X)$, $X=5000,10000,20000,40000$이다.
Height는 primitive integral short model의 $H(E)=\max(4|A|^3,27B^2)$다.
두 ordering의 prime 변수는 모두 $v=p/N(E)$이며 $p\ge5$, $p\nmid N(E)$인 good prime을 쓴다.
Prime bin은 $J_j=[(j+2)/100,(j+3)/100)$, $j=0,\ldots,97$이고 정수 비교로 배정한다.
Weighted trace는 $z=w(E)a_p(E)/(2\sqrt p)$다. Curve별 $\sqrt p\,g_t(z)$와 $w(E)a_p(E)$를
bin에서 합산해 각각 $\mathcal A$와 $B$를 구하며, prime이 없는 curve도 포함한 전체 curve 수로 평균한다.
Unweighted에서는 root number를 곱하지 않는다. Shape는 signed $B$, relative residual은 $|B|$로 나눈다.
SE는 curve 단위 analytic 표준오차이며 isogeny class의 curve multiplicity를 반영한다. 새 bootstrap은 수행하지 않았다.

## 동봉된 결과로 그림·표 재현

저장소 루트에서 Python 3.11 또는 3.12로 실행한다. 이 절차는 동봉 NPZ와 `requirements.txt`의 Python 의존성을 사용한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/bvst_data.py
python -m unittest discover -s tests
python src/make_figures.py
python src/make_tables.py
```

검증에는 두 곡선 집합 입력과 두 NPZ가 모두 필요하다. 하나만 확인하려면 `--family conductor` 또는 `--family height`를 지정한다. 그림과 표는 `work/reproduced/plots/`와 `work/reproduced/tables/`에 저장되며 동봉 파일은 그대로 유지된다.

## 산술 데이터 독립 재계산

전체 계산을 검증한 환경은 WSL/Linux의 SageMath 10.6, Python 3.12.11, NumPy 2.3.2다. 원계산에는 `sage -python`을, 그림과 표 생성에는 위 Python 가상환경을 쓴다. 두 family에서 소규모 계산을 먼저 확인한다.

```bash
sage -python src/recompute_data.py --family conductor --scope smoke --workers 2
sage -python src/recompute_data.py --family height --scope smoke --workers 2
```

재개를 확인하려면 각 family의 새 체크포인트에서 첫 실행에 `--max-batches 1`을 붙인 뒤, 위의 원래 명령을 실행해 완료한다.

전체 재계산은 동봉된 `data/`의 고정 입력을 사용한다.

```bash
sage -python src/recompute_data.py --family conductor --scope full --workers 4
sage -python src/recompute_data.py --family height --scope full --workers 4
python src/bvst_data.py --data-dir work/reproduced/data
python src/make_figures.py --data-dir work/reproduced/data --output-dir work/recomputed/plots
python src/make_tables.py --data-dir work/reproduced/data --output-dir work/recomputed/tables
```

전체 재계산은 동봉 NPZ가 아니라 고정 곡선 목록에서 계수와 root number를 새로 계산한다. 원 저장소, 외부 DB, 기존 계수 캐시는 필요 없다. Conductor 스냅샷은 입력 파일이며 스크립트가 생성하지 않는다. Height 입력을 별도로 생성하려면 `sage -python src/make_height_family.py`를 실행한다(기본 위치: `work/reproduced/inputs/`). 새 입력을 사용하려면 `--family-dir work/reproduced/inputs`와 새 `--work-dir`을 지정한다.

전체 결과의 기본 저장 위치는 `work/reproduced/data/`(`--output-dir`로 변경), 체크포인트는 `work/{scope}_{family}/`(`--work-dir`로 변경)다. SQLite, `progress.json`, `run.json`이 확정된 배치를 기록한다. 같은 명령으로 재개할 수 있지만 입력이나 소스가 바뀌면 체크포인트와 결과 저장 위치를 새로 지정한다. 재생성한 그림이나 표를 이전 파일과 비교할 때도 별도 출력 폴더를 지정한다. 바이트가 다른 기존 파일은 덮어쓰지 않는다.

`--max-seconds 0`은 시간 제한 없음이다. 저장 한도는 기본 10 GiB이며, `--budget-root`를 여러 번 지정하면 해당 경로의 사용량 합계에 한도를 적용한다. Ctrl-C 또는 SIGTERM은 확정 배치 경계에서 중단을 요청한다. 이미 실행 중인 배치가 끝날 때까지 시간이 걸릴 수 있다.


## 입력과 결과의 위치

- `data/conductor_family.json.gz`: LMFDB 고정 snapshot의 329998개 isogeny 대표곡선과 총 496582개 curve의 multiplicity. 출처와 CC BY-SA 4.0 조건은 [데이터 README](data/README.md)에 있다.
- `data/height_family.json.gz`: 동봉 코드가 독립 열거한 primitive 모델 5422개.
- `data/conductor.npz`, `data/height.npz`: 전체 새 계산 결과. Weighted/unweighted·SE·normalizer·pair 수·mask·metadata를 함께 저장한다.
- `data/sample_counts_conductor.csv`, `data/sample_counts_height.csv`, `data/table1_residuals.csv`: 새 결과에서 계산한 세 표.
- `plots/`: 논문용 일곱 그림의 PNG/PDF. 기존 원고 파일명을 유지한다. Figure 1(a)와 Figure 3은 같은 파일이다.

입력 family의 hash·코드 hash·환경·정규화는 SQLite identity와 NPZ의 `metadata_json`에 기록한다.
다른 기존 결과 파일은 자동으로 덮어쓰지 않는다. 긴 내부 작업 이력과 이전 규약의 검증본은 공개 묶음 밖에 보존한다.

| 원고 그림 | `plots/`의 파일명 (PNG와 같은 이름의 PDF 제공) |
| --- | --- |
| Figure 1(a), Figure 3 | `02_normalized_shape_Y40000_full_range.png` |
| Figure 1(b) | `02_normalized_shape_X40000_full_range.png` |
| Figure 1(c) | `05_A_over_B0_all_common_reliable_X40000.png` |
| Figure 1(d) | `03_normalized_shape_X40000_height_unweighted_cm.png` |
| Figure 2 | `01_B_conductor_full_range.png` |
| Figure 4(a) | `01_B_height_full_range.png` |
| Figure 4(b) | `B0_conductor_multiscale_full_range.png` |

Conductor shape의 파일명 `Y40000`은 기존 TeX 호환을 위해 유지하며 그림 내부 scale 표기는 $X$다.
네 normalized shape의 제목·축·범례·colorbar 형식을 통일했고 ordering과 weight에 따른 첨자는 구분한다.

## Bin 선택과 표

Weighted shape는 앞 세 shell 중 둘 이상에서 $|B|>2\operatorname{SE}(B)$를 통과한 discovery와 마지막 shell의 같은 조건을 사용한다.
Unweighted shape는 마지막 shell에서 weighted와 unweighted 두 진폭 조건을 통과한 common bin을 사용하며 discovery를 추가하지 않는다.
$X=40000$의 weighted conductor/height는 96/61개, unweighted conductor/height는 90/17개다.
Height의 unweighted 17개와 weighted 표시 61개의 교집합은 13개다.
Amplitude 그림은 선택 전 98개 bin을 모두 쓴다. 표본/pair 수 표도 선택 전 전체 합이다.
Table 1은 conductor 마지막 shell의 common 집합, 301점 $t$ grid의 사다리꼴 $L^2(0,1)$ norm, bin 방향 linear quartile이다.
Height unweighted 그림은 weighted 표시 집합과 다른 common 집합을 쓰므로 표시 bin 수만으로 noise 수준을 직접 비교하지 않는다.

## 2026-11-03 전체 계산과 검증 완료

공개 코드로 conductor 329998개 대표곡선과 height 5422개 모델의 계수를 모두 새로 계산했다.
4개 worker의 실제 원계산 시간은 conductor 약 2시간 39분, height 약 22분이었다.
일반 계산과 curve 수·curve–prime pair 수·grid·선택 mask가 정확히 일치한다.
평균의 최대 절대 차이는 $1.23\times10^{-13}$ 미만, analytic SE는 $2\times10^{-15}$ 미만이며,
Table 1의 12개 값은 소수점 여섯 자리까지 모두 같다. 완료 후 재개에서도 새 계수/batch가 0개이고 NPZ가 byte 단위로 같았다.

소규모 검증은 직접 점 세기 114건·직접 profile 16건, 경계·multiplicity·평균/SE, 실제 중단/재개와 변조 검출을 포함한다.
원 저장소 자료와 네트워크 읽기를 차단한 분리 복사본에서 두 family의 원계산도 통과했다.
11월 3일 검증은 위의 WSL/Linux 기준 환경에서 수행했다.

## 2026-11-24 새 clone 검증

macOS에서 Python 3.11.5 가상환경을 새로 만들고 NumPy 2.3.2와 Matplotlib 3.10.5를 설치했다. 데이터 검사와 회귀 테스트 3개를 통과했고, 재생성한 CSV 3개는 모두 동봉본과 바이트 단위로 일치했다. 그림 7개는 PNG·PDF 두 형식으로 생성됐다. 같은 Mac 환경에서 기존 생성 코드의 출력과 바이트 단위로 일치했으며, WSL/Linux 기준본과는 렌더링 바이트가 달라질 수 있다.

SageMath 10.4와 NumPy 1.26.3으로 두 family에서 각각 24개 레코드를 2개 worker로 계산했다. 두 실행 모두 첫 배치에서 멈춘 뒤 정상적으로 재개됐다. 완료 후 같은 명령을 반복했을 때 추가 계수와 배치는 0개였고 NPZ 바이트는 같았다.
