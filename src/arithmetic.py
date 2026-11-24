# Compute elliptic curve trace profiles from a frozen family snapshot. run()
# sends batches of at most 64 representatives per shell to calculate_chunk().
# Sage supplies a_p and the root number w, including for CM curves.
# profile() bins good primes p >= 5 by v = p/N(E), and computes each curve's
# A, B, and C using z = w*a_p/(2*sqrt(p)). The weighted and unweighted
# statistics share the same a_p. For the conductor ordering, each isogeny
# class representative contributes with its curve multiplicity.
#
# Coefficients and accumulated moments are committed together to SQLite.
# Resuming checks the input, source hashes and numerical environment.
# finalize() computes curve-level means, standard errors and selection masks.
# Completed NPZ results are written separately from the bundled inputs.

from collections import deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timezone
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import signal
import sqlite3
import sys
import time
import zlib

import numpy as np
from bvst_data import (BASE, SCHEMA, SCALES, check_family, encoded, grid, load_family,
                      pack, sha, unpack)
from reproduction_io import save_outputs

STOP = False
PRIMES = None
T = None


def stop(*_):
    global STOP
    STOP = True


def environment():
    os.environ.setdefault('DOT_SAGE', '/tmp/bvst-public-cm-sage')
    binary = str(Path(sys.executable).resolve().parent)
    if binary not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = binary+os.pathsep+os.environ.get('PATH', '')


def initialize_worker(primes, t):
    global PRIMES, T
    PRIMES, T = primes, t
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def profile(n, primes, ap, w, t):
    """Bin by integer comparisons on [left, right) and use half weight at atoms of g."""
    good = (primes >= 5) & (n % primes != 0) & (100*primes >= 2*n) & (primes < n)
    p, a = primes[good], ap[good].astype(np.int64)
    j = (100*p//n-2).astype(np.int64)
    counts = np.bincount(j, minlength=98).astype(np.int64)
    trace_sum = np.bincount(j, weights=w*a, minlength=98)
    roots = np.sqrt(p)
    z = w*a/(2*roots)
    nonzero = z != 0
    threshold = np.searchsorted(t, np.abs(z[nonzero]), side='left')
    weight = -np.sign(z[nonzero])*roots[nonzero]
    bucket = np.zeros((98, len(t)+1))
    np.add.at(bucket, (j[nonzero], threshold), weight)
    tail = np.cumsum(bucket[:, ::-1], axis=1)[:, ::-1][:, 1:]
    equal = np.zeros(len(threshold), dtype=bool)
    inside = threshold < len(t)
    equal[inside] = t[threshold[inside]] == abs(z[nonzero][inside])
    np.add.at(tail, (j[nonzero][equal], threshold[equal]), .5*weight[equal])
    q = np.log(n*((np.arange(98)+2.5)/100))/(n*.01)
    return {'A': q[:, None]*tail, 'B': q*trace_sum, 'C': q*counts, 'pairs': counts}


def empty(nt):
    return {**{k: np.zeros((98, nt)) for k in ('Aw', 'Au', 'A2')},
            **{k: np.zeros(98) for k in ('Bw', 'Bu', 'B2', 'C', 'C2')},
            'pairs': np.zeros(98, dtype=np.int64)}


def calculate_chunk(job):
    kind, x, start, rows = job
    environment()
    from sage.all import EllipticCurve, QQ
    moments = empty(len(T))
    coefficients = []
    for index, r in enumerate(rows, start):
        began = time.perf_counter()
        e = EllipticCurve(QQ, r['ainvs'])
        n = int(e.conductor())
        assert n == r['conductor'] and bool(e.has_cm()) == r['is_cm']
        w = int(e.root_number())
        if kind == 'height':
            assert w == r['root_number']
            assert e.is_isomorphic(EllipticCurve(QQ, r['primitive_AB']))
        ap = np.asarray(e.aplist(n), dtype='<i4')
        size = int(np.searchsorted(PRIMES, n, side='right'))
        assert len(ap) == size and np.all(ap.astype(np.int64)**2 <= 4*PRIMES[:size])
        d = profile(n, PRIMES[:size], ap, w, T)
        m = r.get('multiplicity', 1)
        # Because g_t is odd, the unweighted A is w times the weighted A; their squares agree.
        for name, values in [('Aw', d['A']), ('Au', w*d['A']), ('A2', d['A']**2),
                             ('Bw', d['B']), ('Bu', w*d['B']), ('B2', d['B']**2),
                             ('C', d['C']), ('C2', d['C']**2), ('pairs', d['pairs'])]:
            moments[name] += m*values
        raw = ap.tobytes()
        coefficients.append((x, index, w, size, zlib.compress(raw),
                             sha(encoded([kind, x, index, w, size])+raw), time.perf_counter()-began))
    return moments, coefficients


def coefficient(db, kind, scale, position):
    r = db.execute('SELECT root,count,ap,sha FROM coefficients WHERE scale=? AND position=?',
                   (scale, position)).fetchone()
    if r is None: raise ValueError('Missing coefficient')
    w, count, compressed, checksum = r
    raw = zlib.decompress(compressed)
    assert len(raw) == count*4 and sha(encoded([kind, scale, position, w, count])+raw) == checksum
    return w, np.frombuffer(raw, dtype='<i4').copy()


def select(rows, scope, sample):
    if scope == 'full': return rows
    chosen = []
    for x in SCALES:
        shell = [r for r in rows if r['scale'] == x]
        for cm in (False, True):
            part = [r for r in shell if r['is_cm'] == cm]
            chosen.extend(part[i] for i in sorted(set(np.linspace(0, len(part)-1, min(sample, len(part)), dtype=int))))
    return sorted(chosen, key=lambda r: (r['scale'], r['conductor'], r['ainvs']))


def finalize(db, kind, rows, identity):
    d = {**grid(kind), 'scales': np.asarray(SCALES), 'trace_divisor': np.asarray(2)}
    parts = []
    for x in SCALES:
        shell = [r for r in rows if r['scale'] == x]
        n = sum(r.get('multiplicity', 1) for r in shell)
        pos, blob, checksum = db.execute('SELECT position,moments,sha FROM states WHERE scale=?', (x,)).fetchone()
        raw = zlib.decompress(blob)
        assert pos == len(shell) and sha(raw) == checksum
        moments = unpack(raw)
        part = {'prime_curve_pairs': moments['pairs'], 'curves': np.asarray(n), 'records': np.asarray(len(shell))}
        for name, sum_key, sq_key in [('A_weighted', 'Aw', 'A2'), ('A_unweighted', 'Au', 'A2'),
                                      ('B_weighted', 'Bw', 'B2'), ('B_unweighted', 'Bu', 'B2'),
                                      ('normalizer', 'C', 'C2')]:
            mean = moments[sum_key]/n
            part[name] = mean
            part['se_'+name] = np.sqrt(np.maximum(moments[sq_key]-moments[sum_key]**2/n, 0)/(n*(n-1)))
        parts.append(part)
    d.update({k: np.stack([p[k] for p in parts]) for k in parts[0]})
    threshold = abs(d['B_weighted']) > 2*d['se_B_weighted']
    d['reliable_discovery_bins'] = threshold[:3].sum(0) >= 2
    d['eligible'] = d['reliable_discovery_bins'] & threshold
    d['common_reliable_bins'] = threshold & (abs(d['B_unweighted']) > 2*d['se_B_unweighted'])
    d['metadata_json'] = np.asarray(encoded(identity).decode())
    return d


def storage_bytes(roots):
    return sum(p.stat().st_size for root in roots for p in Path(root).rglob('*') if p.is_file())


def run(kind, workdir, scope='smoke', workers=1, sample=3, max_seconds=0,
        max_batches=0, budget_roots=(), max_bytes=10*1024**3, root=BASE, *,
        family_dir=None, output_dir=None):
    global STOP
    STOP = False
    environment()
    import sage.version
    from sage.all import prime_range
    root, workdir = Path(root), Path(workdir)
    family_dir = root/'data' if family_dir is None else Path(family_dir)
    if output_dir is None:
        output_dir = root/'work/reproduced/data' if scope == 'full' else workdir
    else:
        output_dir = Path(output_dir)
    all_rows = load_family(kind, root, family_dir=family_dir)
    check_family(kind, all_rows)
    rows = select(all_rows, scope, sample)
    sources = {name: (Path(__file__).parent/name).read_bytes().decode() for name in
               ('arithmetic.py', 'bvst_data.py', 'recompute_data.py', 'reproduction_io.py')}
    identity = {'schema': SCHEMA, 'kind': kind, 'scope': scope, 'sample': sample if scope == 'smoke' else None,
                'family_sha256': sha((family_dir/f'{kind}_family.json.gz').read_bytes()),
                'source_sha256': {name: sha(raw.encode()) for name, raw in sources.items()},
                'sage': sage.version.version, 'numpy': np.__version__,
                'shell': '[X,2X)', 'bins': '(j+2)N<=100p<(j+3)N', 'trace_divisor': 2,
                'prime_regime': 'conductor-scale p/N(E); p>=5 and p does not divide N(E)',
                'seed': None, 'block_records': 64}
    workdir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    handlers = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        with (workdir/'.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            db = sqlite3.connect(workdir/'coefficients.sqlite')
            try:
                db.executescript('CREATE TABLE IF NOT EXISTS metadata(k TEXT PRIMARY KEY,v BLOB);'
                    'CREATE TABLE IF NOT EXISTS coefficients(scale INTEGER,position INTEGER,root INTEGER,count INTEGER,ap BLOB,sha TEXT,seconds REAL,PRIMARY KEY(scale,position));'
                    'CREATE TABLE IF NOT EXISTS states(scale INTEGER PRIMARY KEY,position INTEGER,moments BLOB,sha TEXT,seconds REAL);')
                old = db.execute("SELECT v FROM metadata WHERE k='identity'").fetchone()
                if old: assert bytes(old[0]) == encoded(identity), 'Resume identity mismatch'
                else:
                    with db:
                        db.execute('INSERT INTO metadata VALUES (?,?)', ('identity', encoded(identity)))
                        db.execute('INSERT INTO metadata VALUES (?,?)', ('source_snapshot', zlib.compress(encoded(sources))))
                maximum = max(r['conductor'] for r in rows)
                primes = np.asarray(list(prime_range(2, maximum+1)), dtype=np.int64)
                t = grid(kind)['t_grid']
                initialize_worker(primes, t)
                # Restore the parent handler after starting workers that ignore SIGINT.
                signal.signal(signal.SIGINT, stop)
                status, reason, committed, fresh = 'COMPLETE', None, 0, 0
                last_print = 0.
                pool = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('fork'),
                    initializer=initialize_worker, initargs=(primes, t)) if workers > 1 else None
                try:
                    for x in SCALES:
                        shell = [r for r in rows if r['scale'] == x]
                        old = db.execute('SELECT position,moments,sha,seconds FROM states WHERE scale=?', (x,)).fetchone()
                        pos, moments, seconds = 0, empty(len(t)), 0.
                        if old:
                            pos, blob, checksum, seconds = old
                            raw = zlib.decompress(blob); assert sha(raw) == checksum
                            moments = unpack(raw)
                        assert db.execute('SELECT count(*) FROM coefficients WHERE scale=?', (x,)).fetchone()[0] == pos
                        jobs = iter((kind, x, i, shell[i:i+64]) for i in range(pos, len(shell), 64))
                        pending = deque()
                        def enqueue():
                            try: job = next(jobs)
                            except StopIteration: return False
                            pending.append((job, pool.submit(calculate_chunk, job) if pool else None))
                            return True
                        for _ in range(max(1, workers*2)):
                            if not enqueue(): break
                        while pending:
                            if STOP or (max_seconds and time.perf_counter()-started >= max_seconds) or (max_batches and committed >= max_batches):
                                status, reason = 'PAUSED', 'signal/time/batch limit'
                                break
                            if budget_roots and storage_bytes(budget_roots) > max_bytes-128*1024**2:
                                status, reason = 'STOPPED_STORAGE', '10 GiB storage reserve reached'
                                break
                            job, future = pending.popleft()
                            began = time.perf_counter()
                            part, coefficients = future.result() if future else calculate_chunk(job)
                            for key in moments: moments[key] += part[key]
                            pos += len(coefficients); fresh += len(coefficients); committed += 1
                            seconds += time.perf_counter()-began
                            raw = pack(moments)
                            with db:
                                db.executemany('INSERT INTO coefficients VALUES (?,?,?,?,?,?,?)', coefficients)
                                db.execute('INSERT OR REPLACE INTO states VALUES (?,?,?,?,?)', (x, pos, zlib.compress(raw), sha(raw), seconds))
                            progress = {'kind': kind, 'status': 'RUNNING', 'scale': x, 'position': pos,
                                        'shell_records': len(shell), 'new_coefficients': fresh,
                                        'elapsed_seconds': time.perf_counter()-started,
                                        'sqlite_bytes': (workdir/'coefficients.sqlite').stat().st_size}
                            (workdir/'progress.json').write_bytes(encoded(progress)+b'\n')
                            if time.perf_counter()-last_print > 30 or pos == len(shell):
                                print(json.dumps(progress), flush=True); last_print = time.perf_counter()
                            enqueue()
                        if status != 'COMPLETE':
                            for _, f in pending:
                                if f: f.cancel()
                            break
                finally:
                    if pool: pool.shutdown(wait=True, cancel_futures=True)
                states = [dict(scale=x, records=n) for x, n in db.execute('SELECT scale,position FROM states ORDER BY scale')]
                if sum(s['records'] for s in states) != len(rows) and status == 'COMPLETE': status = 'PAUSED'
                output = None
                if status == 'COMPLETE':
                    result = finalize(db, kind, rows, identity)
                    output = output_dir/f'{kind}.npz'
                    save_outputs(output.parent, {output.name: pack(result)})
                p = workdir/'run.json'
                previous = json.loads(p.read_bytes()) if p.exists() else {'history': []}
                event = {'status': status, 'reason': reason, 'new_coefficients': fresh, 'new_batches': committed,
                         'workers': workers, 'elapsed_seconds': time.perf_counter()-started, 'states': states,
                         'finished_at': datetime.now(timezone.utc).isoformat()}
                report = {'identity': identity, 'status': status, 'records': len(rows), 'history': previous['history']+[event],
                          'output': str(output) if output else None, 'output_sha256': sha(output.read_bytes()) if output else None}
                p.write_bytes(encoded(report)+b'\n')
                (workdir/'progress.json').write_bytes(encoded(event)+b'\n')
                print(json.dumps(event), flush=True)
                return report
            finally:
                db.close()
    finally:
        for sig, handler in handlers.items(): signal.signal(sig, handler)
