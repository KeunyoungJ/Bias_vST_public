"""Regression tests for validation and README inventories (no SageMath needed)."""
import gzip
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import numpy as np

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
import bvst_data as bv


def fixture(root, kind, *, omit=None):
    rows = []
    for scale in bv.SCALES:
        row = {'scale': scale, 'conductor': scale, 'ainvs': [0, 0, 0, 0, 1], 'is_cm': True}
        if kind == 'conductor':
            row.update(lmfdb_iso=f'{scale}.a', multiplicity=2)
        else:
            b = math.isqrt(scale // 27) + 1
            row.update(primitive_AB=[0, b], height=27 * b*b)
        rows.append(row)
    family = gzip.compress(bv.encoded(rows), mtime=0)
    (root/'inputs'/f'{kind}_family.json.gz').write_bytes(family)
    arrays = bv.grid(kind)
    bin_shape = (len(bv.SCALES), len(arrays['v_midpoints']))
    profile_shape = (*bin_shape, len(arrays['t_grid']))
    arrays.update(
        metadata_json=np.asarray(bv.encoded(
            {'schema': bv.SCHEMA, 'kind': kind, 'family_sha256': bv.sha(family)}).decode()),
        scales=np.asarray(bv.SCALES), curves=np.full(len(bv.SCALES), 2 if kind == 'conductor' else 1),
        A_weighted=np.zeros(profile_shape), A_unweighted=np.zeros(profile_shape),
        B_weighted=np.ones(bin_shape), B_unweighted=np.ones(bin_shape),
        se_B_weighted=np.zeros(bin_shape), se_B_unweighted=np.zeros(bin_shape),
        prime_curve_pairs=np.zeros(bin_shape, dtype=int),
        eligible=np.ones(bin_shape, dtype=bool), common_reliable_bins=np.ones(bin_shape, dtype=bool))
    if omit:
        del arrays[omit]
    (root/'results'/f'{kind}.npz').write_bytes(bv.pack(arrays))


class ValidationTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root/'inputs').mkdir()
        (self.root/'results').mkdir()

    def cli(self, *args, optimized=False):
        return subprocess.run(
            [sys.executable, *(['-O'] if optimized else []), str(SRC/'bvst_data.py'),
             '--family-dir', str(self.root/'inputs'), '--data-dir', str(self.root/'results'), *args],
            capture_output=True, text=True, check=False)

    def test_empty_and_partial_fail_but_explicit_one_family_passes(self):
        empty = self.cli()
        self.assertEqual(empty.returncode, 1)
        self.assertIn('conductor_family.json.gz', empty.stderr)
        self.assertIn('height.npz', empty.stderr)
        self.assertNotIn('PASS', empty.stdout)
        fixture(self.root, 'height')
        partial = self.cli()
        self.assertEqual(partial.returncode, 1)
        self.assertIn('conductor.npz', partial.stderr)
        selected = self.cli('--family', 'height')
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(list(json.loads(selected.stdout)['families']), ['height'])
        fixture(self.root, 'conductor')
        full = self.cli()
        self.assertEqual(full.returncode, 0, full.stderr)
        self.assertEqual(list(json.loads(full.stdout)['families']), ['conductor', 'height'])

    def test_missing_required_payload_and_bad_hash_fail(self):
        fixture(self.root, 'height', omit='A_weighted')
        missing = self.cli('--family', 'height')
        self.assertEqual(missing.returncode, 1)
        self.assertIn('A_weighted', missing.stderr)
        fixture(self.root, 'height')
        family = self.root/'inputs'/'height_family.json.gz'
        family.write_bytes(gzip.compress(gzip.decompress(family.read_bytes()), mtime=1))
        tampered = self.cli('--family', 'height', optimized=True)
        self.assertEqual(tampered.returncode, 1)
        self.assertIn('SHA-256', tampered.stderr)


class ReadmeTest(unittest.TestCase):
    def test_nested_and_standalone_layouts_and_idempotence(self):
        for standalone in (False, True):
            with self.subTest(standalone=standalone), TemporaryDirectory() as temp:
                root = Path(temp)
                english, korean = (('README.md', 'README.ko.md') if standalone else
                                   ('README.en.md', 'README.md'))
                for name in (english, korean):
                    (root/name).write_text('# Title\n\nOutside of the inventory.\n', encoding='utf-8')
                files = ('.git/objects/pack.bin', 'work/run/report.json',
                         'src/.ipynb_checkpoints/copy.py', 'src/__pycache__/code.pyc',
                         'data/kept file.csv', '.DS_Store')
                for name in files:
                    path = root/name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
                (root/'data/README.md').touch()
                bv.refresh_readme(root)
                en = (root/english).read_text(encoding='utf-8')
                ko = (root/korean).read_text(encoding='utf-8')
                prefix = '' if standalone else 'public_release/'
                self.assertIn('## File inventory and roles', en)
                self.assertIn('## 현재 파일 위치와 역할', ko)
                self.assertIn(f'[{prefix}data/kept file.csv](data/kept%20file.csv)', en)
                self.assertIn(f'[{prefix}{korean}]({korean}) | Korean README', en)
                self.assertIn(f'[{prefix}data/README.md](data/README.md) | Conductor snapshot provenance and license', en)
                self.assertIn('Outside of the inventory.', en)
                for name in files[:-2]+files[-1:]:
                    self.assertNotIn(Path(name).name, en)
                os.utime(root/english, ns=(1_000_000_000, 1_000_000_000))
                bv.refresh_readme(root)
                self.assertEqual((root/english).stat().st_mtime_ns, 1_000_000_000)


if __name__ == '__main__':
    unittest.main()
