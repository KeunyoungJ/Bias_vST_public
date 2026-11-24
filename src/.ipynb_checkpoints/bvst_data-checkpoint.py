# 공개 폴더의 입력과 집계 결과를 읽는 공통 함수가 모여 있다.
# BASE는 public_release/를 가리키고, SCALES는 네 shell의 시작값을 담는다.
# grid()는 profile을 평가하는 t 격자와 v = p/N(E)의 bin 경계·중점을 돌려준다.
#
# load_family()는 data/{family}_family.json.gz에서 곡선 목록을 읽는다.
# 이 목록은 arithmetic.py의 run()이 사용하고, height 쪽은 make_height_family.py에서 만든다.
# load_profiles()는 data/{family}.npz의 집계 배열을 그림·표 코드에 넘긴다.
# pack()과 unpack()은 배열을 NPZ 바이트로 저장하고 다시 읽는 함수다.
#
# public_release/에서 python src/bvst_data.py를 실행하면 verify()가 JSON으로 결과를 출력한다.
# 존재하는 곡선 목록과 대응 NPZ를 대상으로 입력 해시, 곡선 수, 격자, bin 선택을 확인한다.
# refresh_readme()는 산출물을 만드는 코드에서 호출하며 한글·영문 README의 파일 목록을 갱신한다.

"""공개본의 명시적 계산 규약, 입력 loader와 README 파일 목록."""
from pathlib import Path
from io import BytesIO
import gzip
import hashlib
import json
import os

import numpy as np

BASE = Path(__file__).resolve().parents[1]
SCALES = (5000, 10000, 20000, 40000)
SCHEMA = 'bvst-cm-inclusive-v2'


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def grid(kind):
    return {'t_grid': np.linspace(0, 1, 301 if kind == 'conductor' else 401),
            'v_edges': np.arange(2, 101) / 100,
            'v_midpoints': (np.arange(98) + 2.5) / 100}


def load_family(kind, root=BASE):
    if kind not in ('conductor', 'height'):
        raise ValueError(kind)
    return json.loads(gzip.decompress((Path(root) / f'data/{kind}_family.json.gz').read_bytes()))


def load_profiles(kind, root=BASE):
    with np.load(Path(root) / f'data/{kind}.npz', allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}


def pack(arrays):
    f = BytesIO()
    np.savez_compressed(f, **{k: arrays[k] for k in sorted(arrays)})
    return f.getvalue()


def unpack(raw):
    with np.load(BytesIO(raw), allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}


def check_family(kind, rows):
    identities = set()
    for r in rows:
        value = r['conductor'] if kind == 'conductor' else r['height']
        assert r['scale'] in SCALES and r['scale'] <= value < 2*r['scale']
        assert len(r['ainvs']) == 5 and isinstance(r['is_cm'], bool)
        assert r['conductor'] > 0 and r.get('multiplicity', 1) > 0
        key = r['lmfdb_iso'] if kind == 'conductor' else tuple(r['primitive_AB'])
        assert key not in identities
        identities.add(key)
        if kind == 'height':
            a, b = r['primitive_AB']
            assert max(4*abs(a)**3, 27*b*b) == value and 4*a**3+27*b*b != 0
    return [{'X': x, 'records': sum(r['scale'] == x for r in rows),
             'curves': sum(r.get('multiplicity', 1) for r in rows if r['scale'] == x)}
            for x in SCALES]


def verify(root=BASE):
    result = {}
    for kind in ('conductor', 'height'):
        if not (Path(root) / f'data/{kind}_family.json.gz').exists():
            continue
        rows = load_family(kind, root)
        result[kind] = check_family(kind, rows)
        if not (Path(root) / f'data/{kind}.npz').exists():
            continue
        d = load_profiles(kind, root)
        meta = json.loads(str(d['metadata_json']))
        assert meta['schema'] == SCHEMA and meta['kind'] == kind
        assert meta['family_sha256'] == sha((Path(root)/f'data/{kind}_family.json.gz').read_bytes())
        np.testing.assert_array_equal(d['scales'], SCALES)
        np.testing.assert_array_equal(d['curves'], [a['curves'] for a in result[kind]])
        for key, values in grid(kind).items():
            np.testing.assert_array_equal(d[key], values)
        for key, values in d.items():
            if values.dtype.kind in 'fiu':
                assert np.isfinite(values).all(), key
        threshold = abs(d['B_weighted']) > 2*d['se_B_weighted']
        discovery = threshold[:3].sum(0) >= 2
        np.testing.assert_array_equal(d['eligible'], discovery & threshold)
        np.testing.assert_array_equal(d['common_reliable_bins'],
            threshold & (abs(d['B_unweighted']) > 2*d['se_B_unweighted']))
    return {'status': 'PASS', 'families': result}


def refresh_readme(root=BASE):
    """보존 파일이 추가될 때 README 자신의 경로도 포함해 목록을 갱신한다."""
    root = Path(root)
    p = root/'README.md'
    if not p.exists():
        p.write_text('# 타원곡선 수치 실험 재현\n\n')
    files = sorted(f for f in root.rglob('*') if f.is_file() and
                   not any(v in ('.cache', '__pycache__', '.venv') for v in f.relative_to(root).parts)
                   and f.name != '.lock' and not f.name.endswith(('-journal', '-wal', '-shm', '.tmp')))
    roles = {'README.en.md': '영어판: 파일 목록·환경·실행 순서·규약',
             'README.md': '이 문서: 현재 파일 목록·환경·실행 순서·규약',
             'requirements.txt': 'Python 의존성 버전; SageMath는 별도 설치',
             '.gitignore': '임시 cache·lock·SQLite journal 제외',
             '.gitattributes': '텍스트 LF·배열 및 압축 파일의 binary 처리'}
    source_roles = {'arithmetic.py': '동일 loop의 원계산·curve SE·SQLite 재개',
        'recompute_data.py': 'conductor/height를 독립 실행하는 원계산 진입점',
        'bvst_data.py': '명시적 규약·입력/결과 loader·검사·이 파일 목록 갱신',
        'make_height_family.py': 'primitive short model 전체 독립 열거',
        'make_figures.py': '새 전체 계산 자료에서 일곱 논문 그림 생성',
        'make_tables.py': '표본 수·pair 수·Table 1 CSV 생성',
        'trace_normalization.py': 'tilt/translation template와 trace 규약',
        'reproduction_io.py': '다른 기존 출력 보존·동일 출력 재사용'}
    def role(f):
        name = f.name
        if name in roles: return roles[name]
        if f.parent.name == 'src': return source_roles.get(name, 'Python 코드')
        if name.endswith('_family.json.gz'): return '고정 곡선 목록 입력'
        if name in ('conductor.npz', 'height.npz'): return '새 전체 계산의 weighted/unweighted·SE·pair 수·mask'
        if name.startswith('sample_counts_'): return 'shell별 curve 수·curve–prime pair 수'
        if name.startswith('table1_residuals'): return 'common bin에서 계산한 잔차 사분위수'
        if f.suffix in ('.png', '.pdf'): return '논문 그림: '+('300 dpi PNG' if f.suffix == '.png' else 'vector PDF')
        if f.suffix == '.sqlite': return '보존 계수·누적 상태·재개 정보'
        return '생성 자료·실행 기록'
    english_roles = {
        '이 문서: 현재 파일 목록·환경·실행 순서·규약': 'Korean README: file inventory, environment, execution order, and conventions',
        '영어판: 파일 목록·환경·실행 순서·규약': 'English README: file inventory, environment, execution order, and conventions',
        'Python 의존성 버전; SageMath는 별도 설치': 'Python dependency versions; install SageMath separately',
        '임시 cache·lock·SQLite journal 제외': 'Excludes temporary caches, locks, and SQLite journals',
        '텍스트 LF·배열 및 압축 파일의 binary 처리': 'LF text files; binary handling for arrays and compressed files',
        '동일 loop의 원계산·curve SE·SQLite 재개': 'Arithmetic computation, curve-level SE, and SQLite-based resumption',
        'conductor/height를 독립 실행하는 원계산 진입점': 'Entry point for independent conductor and height computations',
        '명시적 규약·입력/결과 loader·검사·이 파일 목록 갱신': 'Conventions, input/result loaders, validation, and README inventory updates',
        'primitive short model 전체 독립 열거': 'Independent enumeration of all primitive short models',
        '새 전체 계산 자료에서 일곱 논문 그림 생성': 'Generates seven paper figures from the full computation results',
        '표본 수·pair 수·Table 1 CSV 생성': 'Generates sample counts, pair counts, and Table 1 as CSV files',
        'tilt/translation template와 trace 규약': 'Tilt/translation templates and trace conventions',
        '다른 기존 출력 보존·동일 출력 재사용': 'Preserves different existing outputs and reuses identical outputs',
        'Python 코드': 'Python code',
        '고정 곡선 목록 입력': 'Frozen curve-family input',
        '새 전체 계산의 weighted/unweighted·SE·pair 수·mask': 'Full computation results: weighted/unweighted statistics, SE, pair counts, and masks',
        'shell별 curve 수·curve–prime pair 수': 'Curve and curve–prime pair counts by shell',
        'common bin에서 계산한 잔차 사분위수': 'Residual quartiles over the common bins',
        '논문 그림: 300 dpi PNG': 'Paper figure: 300 dpi PNG',
        '논문 그림: vector PDF': 'Paper figure: vector PDF',
        '보존 계수·누적 상태·재개 정보': 'Preserved coefficients, accumulated state, and resumption information',
        '생성 자료·실행 기록': 'Generated data and execution records',
    }
    def tree(directory, prefix=''):
        children = sorted({f.relative_to(directory).parts[0] for f in files if f.is_relative_to(directory)})
        lines = []
        for i, name in enumerate(children):
            child = directory/name
            last = i == len(children)-1
            lines.append(prefix+('└── ' if last else '├── ')+name+('/' if child.is_dir() else '')+'\n')
            if child.is_dir():
                lines.extend(tree(child, prefix+('    ' if last else '│   ')))
        return lines
    tree_text = ''.join(tree(root))
    for filename in ('README.md', 'README.en.md'):
        p = root/filename
        if not p.exists():
            continue
        english = filename == 'README.en.md'
        block = '<!-- FILES_BEGIN -->\n<a id="file-map"></a>\n\n'
        if english:
            block += '## File inventory and roles\n\n'
            block += f'The package currently contains **{len(files)} files**, including both READMEs. Paths in the table are relative to the repository root.\n'
            block += 'Update this inventory and the input/output descriptions whenever files are added, removed, moved, or renamed.\n'
        else:
            block += '## 현재 파일 위치와 역할\n\n'
            block += f'두 README를 포함한 현재 보존 파일은 **{len(files)}개**다. 표의 경로는 저장소 루트 기준이다.\n'
            block += '파일을 추가·삭제·이동·이름 변경할 때 이 목록과 입출력 설명을 함께 갱신한다.\n'
        block += '\n```text\npublic_release/\n'+tree_text+'```\n\n'
        block += '| File path | Role |\n| --- | --- |\n' if english else '| 파일 경로 | 역할 |\n| --- | --- |\n'
        for f in files:
            name = str(f.relative_to(root))
            description = english_roles[role(f)] if english else role(f)
            block += f'| [public_release/{name}]({name}) | {description} |\n'
        block += '\n<!-- FILES_END -->\n'
        text = p.read_text()
        if '<!-- FILES_BEGIN -->' in text:
            a = text.index('<!-- FILES_BEGIN -->'); b = text.index('<!-- FILES_END -->')+len('<!-- FILES_END -->')
            text = text[:a]+block.rstrip()+text[b:]
        else:
            a = text.index('\n')+1
            text = text[:a]+'\n'+block+text[a:]
        p.write_text(text)



if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
