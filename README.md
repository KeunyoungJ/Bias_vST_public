# 타원곡선 수치 실험 재현

[English version](README.en.md)

<!-- FILES_BEGIN -->
<a id="file-map"></a>

## 현재 파일 위치와 역할

두 README를 포함한 현재 보존 파일은 **34개**다. 표의 경로는 저장소 루트 기준이다.
파일을 추가·삭제·이동·이름 변경할 때 이 목록과 입출력 설명을 함께 갱신한다.

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

| 파일 경로 | 역할 |
| --- | --- |
| [public_release/.gitattributes](.gitattributes) | 텍스트 LF·배열 및 압축 파일의 binary 처리 |
| [public_release/.gitignore](.gitignore) | 임시 cache·lock·SQLite journal 제외 |
| [public_release/README.en.md](README.en.md) | 영어판: 파일 목록·환경·실행 순서·규약 |
| [public_release/README.md](README.md) | 이 문서: 현재 파일 목록·환경·실행 순서·규약 |
| [public_release/data/conductor.npz](data/conductor.npz) | 새 전체 계산의 weighted/unweighted·SE·pair 수·mask |
| [public_release/data/conductor_family.json.gz](data/conductor_family.json.gz) | 고정 곡선 목록 입력 |
| [public_release/data/height.npz](data/height.npz) | 새 전체 계산의 weighted/unweighted·SE·pair 수·mask |
| [public_release/data/height_family.json.gz](data/height_family.json.gz) | 고정 곡선 목록 입력 |
| [public_release/data/sample_counts_conductor.csv](data/sample_counts_conductor.csv) | shell별 curve 수·curve–prime pair 수 |
| [public_release/data/sample_counts_height.csv](data/sample_counts_height.csv) | shell별 curve 수·curve–prime pair 수 |
| [public_release/data/table1_residuals.csv](data/table1_residuals.csv) | common bin에서 계산한 잔차 사분위수 |
| [public_release/plots/01_B_conductor_full_range.pdf](plots/01_B_conductor_full_range.pdf) | 논문 그림: vector PDF |
| [public_release/plots/01_B_conductor_full_range.png](plots/01_B_conductor_full_range.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/01_B_height_full_range.pdf](plots/01_B_height_full_range.pdf) | 논문 그림: vector PDF |
| [public_release/plots/01_B_height_full_range.png](plots/01_B_height_full_range.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/02_normalized_shape_X40000_full_range.pdf](plots/02_normalized_shape_X40000_full_range.pdf) | 논문 그림: vector PDF |
| [public_release/plots/02_normalized_shape_X40000_full_range.png](plots/02_normalized_shape_X40000_full_range.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/02_normalized_shape_Y40000_full_range.pdf](plots/02_normalized_shape_Y40000_full_range.pdf) | 논문 그림: vector PDF |
| [public_release/plots/02_normalized_shape_Y40000_full_range.png](plots/02_normalized_shape_Y40000_full_range.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/03_normalized_shape_X40000_height_unweighted_cm.pdf](plots/03_normalized_shape_X40000_height_unweighted_cm.pdf) | 논문 그림: vector PDF |
| [public_release/plots/03_normalized_shape_X40000_height_unweighted_cm.png](plots/03_normalized_shape_X40000_height_unweighted_cm.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/05_A_over_B0_all_common_reliable_X40000.pdf](plots/05_A_over_B0_all_common_reliable_X40000.pdf) | 논문 그림: vector PDF |
| [public_release/plots/05_A_over_B0_all_common_reliable_X40000.png](plots/05_A_over_B0_all_common_reliable_X40000.png) | 논문 그림: 300 dpi PNG |
| [public_release/plots/B0_conductor_multiscale_full_range.pdf](plots/B0_conductor_multiscale_full_range.pdf) | 논문 그림: vector PDF |
| [public_release/plots/B0_conductor_multiscale_full_range.png](plots/B0_conductor_multiscale_full_range.png) | 논문 그림: 300 dpi PNG |
| [public_release/requirements.txt](requirements.txt) | Python 의존성 버전; SageMath는 별도 설치 |
| [public_release/src/arithmetic.py](src/arithmetic.py) | 동일 loop의 원계산·curve SE·SQLite 재개 |
| [public_release/src/bvst_data.py](src/bvst_data.py) | 명시적 규약·입력/결과 loader·검사·이 파일 목록 갱신 |
| [public_release/src/make_figures.py](src/make_figures.py) | 새 전체 계산 자료에서 일곱 논문 그림 생성 |
| [public_release/src/make_height_family.py](src/make_height_family.py) | primitive short model 전체 독립 열거 |
| [public_release/src/make_tables.py](src/make_tables.py) | 표본 수·pair 수·Table 1 CSV 생성 |
| [public_release/src/recompute_data.py](src/recompute_data.py) | conductor/height를 독립 실행하는 원계산 진입점 |
| [public_release/src/reproduction_io.py](src/reproduction_io.py) | 다른 기존 출력 보존·동일 출력 재사용 |
| [public_release/src/trace_normalization.py](src/trace_normalization.py) | tilt/translation template와 trace 규약 |

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

## 환경과 실행 순서

확인 환경: Python 3.12.11, SageMath 10.6, NumPy 2.3.2, Matplotlib 3.10.5, WSL/Linux.
`requirements.txt`는 Python package 버전이며 SageMath는 별도로 설치한다. Sage Python에서 실행한다.
아래 명령은 `public_release/` 안에서 실행한다. 원 저장소·일반 계산의 계수 cache·외부 DB 연결은 필요 없다.

```bash
python src/make_height_family.py
python src/bvst_data.py
python src/recompute_data.py --family conductor --scope full --workers 4
python src/recompute_data.py --family height --scope full --workers 4
python src/make_figures.py
python src/make_tables.py
```

`--scope full`은 전체 family의 계수와 root number를 새로 계산한다. 기존 집계 결과를 복사하지 않는다.
`--work-dir`로 계수/재개 SQLite의 위치를 지정할 수 있다. 기본은 `work/{scope}_{family}/`다.
보존 SQLite와 `progress.json`·`run.json`은 계산/재개 기록이며 단순 cache가 아니다.
같은 명령을 다시 실행하면 확정 batch 다음부터 재개한다. 완료 재개는 새 계수를 만들지 않는다.
`--max-seconds 0`은 시간 상한 없음이며, `--max-bytes` 기본은 10 GiB다.
`--budget-root`를 반복 지정하면 관련 저장 경로의 합에 대해 예산을 적용한다. 계수와 moments는 같은 transaction으로 확정한다.
긴 실행 전에 저장량을 확인한다. SIGTERM/Ctrl-C는 확정 batch 경계에서 중단한다.
Conductor와 height의 checkpoint identity는 분리되어 다른 family 실행 때문에 재계산하지 않는다.
파일이 생성되면 최상단 목록을 갱신한다. 마지막 그림·표 생성 후 목록에서 전체 산출물 위치를 확인할 수 있다.

## 입력과 결과의 위치

- `data/conductor_family.json.gz`: LMFDB 고정 snapshot의 329998개 isogeny 대표곡선과 총 496582개 curve의 multiplicity.
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
이는 현재 Sage 환경에서의 독립 실행 검증이며 새 운영체제에서 의존성 설치까지 검증한 것은 아니다.
이전 공개 준비본은 내부 보존 archive로 옮겨 hash 복원을 확인했다. 아직 원격 배포하지 않았다.

## Git에서 제외한 내부 계수 DB

전체 원계산의 계수 DB 두 파일은 공개 폴더 밖에 로컬 보존하며 Git에 포함하지 않는다.
위 공개본 34개 파일 목록에는 이 내부 DB를 포함하지 않는다.

- `results/current/elliptic_curves/public_cm_20261103-002218/checkpoint/conductor/coefficients.sqlite`: 약 2.54 GiB.
- `results/current/elliptic_curves/public_cm_20261103-002218/checkpoint/height/coefficients.sqlite`: 약 301.06 MiB.

두 경로는 저장소 루트 기준이다. 새 clone에서는 위 실행 순서의 `--scope full` 명령으로 DB를 재생성한다.
그림·표 생성에는 동봉 NPZ를 사용할 수 있다. 기존 DB를 재사용하려면 별도 보존한 파일이 필요하다.
