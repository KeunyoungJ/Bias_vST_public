# Shared readers for frozen curve-family inputs and aggregated results.
# BASE is the package root, and SCALES gives the four shell lower bounds.
# grid() provides the profile grid in t and the bin edges and midpoints in v = p/N(E).
#
# arithmetic.py reads the family snapshots; make_height_family.py builds the height snapshot.
# The figure and table scripts read the aggregated arrays. pack() and unpack() handle NPZ bytes.
# Running this file validates the snapshots, results, and bin selection without SageMath.
# Output scripts can update the inventory blocks in both READMEs with refresh_readme().

import argparse
from pathlib import Path
from io import BytesIO
import gzip
import hashlib
import json
import os
from zipfile import BadZipFile
from urllib.parse import quote

import numpy as np

BASE = Path(__file__).resolve().parents[1]
SCALES = (5000, 10000, 20000, 40000)
SCHEMA = 'bvst-cm-inclusive-v2'
KINDS = ('conductor', 'height')


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def grid(kind):
    return {'t_grid': np.linspace(0, 1, 301 if kind == 'conductor' else 401),
            'v_edges': np.arange(2, 101) / 100,
            'v_midpoints': (np.arange(98) + 2.5) / 100}


def _data_path(kind, filename, root, directory):
    if kind not in KINDS:
        raise ValueError(f'Unknown curve family: {kind}')
    base = Path(directory) if directory is not None else Path(root) / 'data'
    return base / filename.format(kind=kind)


def load_family(kind, root=BASE, *, family_dir=None):
    path = _data_path(kind, '{kind}_family.json.gz', root, family_dir)
    return json.loads(gzip.decompress(path.read_bytes()))


def load_profiles(kind, root=BASE, *, data_dir=None):
    path = _data_path(kind, '{kind}.npz', root, data_dir)
    with np.load(path, allow_pickle=False) as z:
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
        if r['scale'] not in SCALES or not r['scale'] <= value < 2*r['scale']:
            raise ValueError(f'{kind}: invalid shell for value {value}')
        if len(r['ainvs']) != 5 or not isinstance(r['is_cm'], bool):
            raise ValueError(f'{kind}: invalid invariants or CM flag')
        if r['conductor'] <= 0 or r.get('multiplicity', 1) <= 0:
            raise ValueError(f'{kind}: nonpositive conductor or multiplicity')
        key = r['lmfdb_iso'] if kind == 'conductor' else tuple(r['primitive_AB'])
        if key in identities:
            raise ValueError(f'{kind}: duplicate family record {key}')
        identities.add(key)
        if kind == 'height':
            a, b = r['primitive_AB']
            if max(4*abs(a)**3, 27*b*b) != value or 4*a**3+27*b*b == 0:
                raise ValueError(f'{kind}: invalid height model for coefficients {(a, b)}')
    return [{'X': x, 'records': sum(r['scale'] == x for r in rows),
             'curves': sum(r.get('multiplicity', 1) for r in rows if r['scale'] == x)}
            for x in SCALES]


def verify(root=BASE, *, data_dir=None, family_dir=None, kinds=KINDS):
    """Validate every requested family; no required input or result may be missing."""
    kinds = tuple(dict.fromkeys(kinds))
    if not kinds:
        raise ValueError('Select at least one curve family to validate.')
    paths = {}
    for kind in kinds:
        paths[kind] = (
            _data_path(kind, '{kind}_family.json.gz', root, family_dir),
            _data_path(kind, '{kind}.npz', root, data_dir),
        )
    missing = [str(p) for pair in paths.values() for p in pair if not p.is_file()]
    if missing:
        raise FileNotFoundError('Missing required files: ' + ', '.join(missing))

    result = {}
    for kind, (input_path, _) in paths.items():
        snapshot = input_path.read_bytes()
        rows = json.loads(gzip.decompress(snapshot))
        if not rows:
            raise ValueError(f'{kind}: the family snapshot is empty')
        result[kind] = check_family(kind, rows)
        d = load_profiles(kind, root, data_dir=data_dir)
        meta = json.loads(str(d['metadata_json']))
        if meta['schema'] != SCHEMA or meta['kind'] != kind:
            raise ValueError(f'{kind}: incompatible results schema or family')
        if meta['family_sha256'] != sha(snapshot):
            raise ValueError(f'{kind}: results do not match the family snapshot (SHA-256)')

        np.testing.assert_array_equal(d['scales'], SCALES)
        np.testing.assert_array_equal(d['curves'], [a['curves'] for a in result[kind]])
        expected_grid = grid(kind)
        for key, values in expected_grid.items():
            np.testing.assert_array_equal(d[key], values, err_msg=f'{kind}: invalid {key}')

        # Check that the arrays consumed by the plot and table scripts are present and usable.
        bin_shape = (len(SCALES), len(expected_grid['v_midpoints']))
        profile_shape = (*bin_shape, len(expected_grid['t_grid']))
        for key in ('A_weighted', 'A_unweighted'):
            if d[key].shape != profile_shape or d[key].dtype.kind not in 'fiu':
                raise ValueError(f'{kind}: invalid shape or type for {key}, expected {profile_shape}')
        for key in ('B_weighted', 'B_unweighted', 'se_B_weighted', 'se_B_unweighted',
                    'prime_curve_pairs', 'eligible', 'common_reliable_bins'):
            expected_type = ('b' if key in ('eligible', 'common_reliable_bins') else
                             'iu' if key == 'prime_curve_pairs' else 'fiu')
            if d[key].shape != bin_shape or d[key].dtype.kind not in expected_type:
                raise ValueError(f'{kind}: invalid shape or type for {key}, expected {bin_shape}')
        for key, values in d.items():
            if values.dtype.kind in 'fiu' and not np.isfinite(values).all():
                raise ValueError(f'{kind}: non-finite values in {key}')
        threshold = abs(d['B_weighted']) > 2*d['se_B_weighted']
        discovery = threshold[:3].sum(0) >= 2
        np.testing.assert_array_equal(d['eligible'], discovery & threshold)
        np.testing.assert_array_equal(d['common_reliable_bins'],
            threshold & (abs(d['B_unweighted']) > 2*d['se_B_unweighted']))
    return {'status': 'PASS', 'families': result}


def refresh_readme(root=BASE):
    """Refresh the shipped file inventory in both README language versions."""
    root = Path(root)
    standalone = (root/'README.ko.md').is_file() or (
        not (root/'README.en.md').is_file() and (root/'.git').exists())
    english_readme, korean_readme = (
        ('README.md', 'README.ko.md') if standalone else ('README.en.md', 'README.md'))
    display_prefix = '' if standalone else 'public_release/'
    ignored_dirs = {'.git', '.cache', '.venv', '.ipynb_checkpoints', '.pytest_cache',
                    '__pycache__', 'work'}
    ignored_files = {'.git', '.lock', '.DS_Store'}
    ignored_suffixes = ('-journal', '-wal', '-shm', '.tmp', '.pyc', '.pyo', '.sqlite')
    files = []
    for directory, dirs, names in os.walk(root):
        # Prune before traversing large Git, cache, and computation directories.
        directory = Path(directory)
        dirs[:] = [name for name in dirs
                   if name not in ignored_dirs and not (directory/name).is_symlink()]
        files.extend(directory/name for name in names
                     if name not in ignored_files
                     and not name.endswith(ignored_suffixes)
                     and (directory/name).is_file() and not (directory/name).is_symlink())
    files.sort()
    roles = {english_readme: '영어판: 파일 목록·환경·실행 순서·규약',
             korean_readme: '한국어판: 파일 목록·환경·실행 순서·규약',
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
        if f.parent.name == 'tests': return '재현 코드 회귀 테스트'
        if name.endswith('_family.json.gz'): return '고정 곡선 목록 입력'
        if name in ('conductor.npz', 'height.npz'): return '새 전체 계산의 weighted/unweighted·SE·pair 수·mask'
        if name.startswith('sample_counts_'): return 'shell별 curve 수·curve–prime pair 수'
        if name.startswith('table1_residuals'): return 'common bin에서 계산한 잔차 사분위수'
        if f.suffix in ('.png', '.pdf'): return '논문 그림: '+('300 dpi PNG' if f.suffix == '.png' else 'vector PDF')
        return '생성 자료·실행 기록'
    english_roles = {
        '한국어판: 파일 목록·환경·실행 순서·규약': 'Korean README: file inventory, environment, execution order, and conventions',
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
        '재현 코드 회귀 테스트': 'Reproduction code regression tests',
        '고정 곡선 목록 입력': 'Frozen curve-family input',
        '새 전체 계산의 weighted/unweighted·SE·pair 수·mask': 'Full computation results: weighted/unweighted statistics, SE, pair counts, and masks',
        'shell별 curve 수·curve–prime pair 수': 'Curve and curve–prime pair counts by shell',
        'common bin에서 계산한 잔차 사분위수': 'Residual quartiles over the common bins',
        '논문 그림: 300 dpi PNG': 'Paper figure: 300 dpi PNG',
        '논문 그림: vector PDF': 'Paper figure: vector PDF',
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
    for filename in (english_readme, korean_readme):
        p = root/filename
        if not p.exists():
            continue
        english = filename == english_readme
        block = '<!-- FILES_BEGIN -->\n<a id="file-map"></a>\n\n'
        if english:
            block += '## File inventory and roles\n\n'
            block += f'The package inventory lists **{len(files)} files**. Paths in the table are relative to the repository root.\n'
            block += 'Update this inventory and the input/output descriptions whenever files are added, removed, moved, or renamed.\n'
        else:
            block += '## 현재 파일 위치와 역할\n\n'
            block += f'현재 파일 목록에는 **{len(files)}개**의 파일이 있다. 표의 경로는 저장소 루트 기준이다.\n'
            block += '파일을 추가·삭제·이동·이름 변경할 때 이 목록과 입출력 설명을 함께 갱신한다.\n'
        block += '\n```text\n'+(display_prefix or './')+'\n'+tree_text+'```\n\n'
        block += '| File path | Role |\n| --- | --- |\n' if english else '| 파일 경로 | 역할 |\n| --- | --- |\n'
        for f in files:
            name = f.relative_to(root).as_posix()
            description = english_roles[role(f)] if english else role(f)
            block += f'| [{display_prefix}{name}]({quote(name)}) | {description} |\n'
        block += '\n<!-- FILES_END -->\n'
        original = p.read_text(encoding='utf-8')
        begin, end = '<!-- FILES_BEGIN -->', '<!-- FILES_END -->'
        if begin in original and end in original:
            a = original.index(begin)
            b = original.index(end, a) + len(end)
            updated = original[:a] + block.rstrip() + original[b:]
        elif begin in original or end in original:
            raise ValueError(f'Unpaired inventory markers in {p}')
        else:
            heading, sep, body = original.partition('\n')
            updated = heading + (sep or '\n') + '\n' + block + body
        if updated != original:
            p.write_text(updated, encoding='utf-8', newline='\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate bundled or recomputed numerical data.')
    parser.add_argument('--data-dir', type=Path, help='Directory containing the NPZ results.')
    parser.add_argument('--family-dir', type=Path, help='Directory containing the frozen family inputs.')
    parser.add_argument('--family', action='append', choices=KINDS,
                        help='Validate one family; repeat for both (default: both).')
    args = parser.parse_args(argv)
    try:
        result = verify(data_dir=args.data_dir, family_dir=args.family_dir, kinds=args.family or KINDS)
    except (OSError, ValueError, KeyError, TypeError, EOFError, BadZipFile, AssertionError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
