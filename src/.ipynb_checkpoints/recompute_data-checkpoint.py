"""CM 포함 conductor 또는 height를 독립 실행한다. 기본은 소규모 smoke다."""
import argparse
from pathlib import Path
from bvst_data import BASE


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family', choices=['conductor', 'height'], required=True)
    p.add_argument('--scope', choices=['smoke', 'full'], default='smoke')
    p.add_argument('--work-dir', type=Path)
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--sample', type=int, default=3, help='CM/non-CM 각각 shell당 결정론적 표본 수')
    p.add_argument('--max-seconds', type=float, default=0, help='0이면 시간 상한 없음')
    p.add_argument('--max-batches', type=int, default=0)
    p.add_argument('--budget-root', type=Path, action='append', default=[])
    p.add_argument('--max-bytes', type=int, default=10*1024**3)
    a = p.parse_args()
    assert a.workers >= 1 and a.sample >= 2
    work = a.work_dir or BASE/'work'/f'{a.scope}_{a.family}'
    candidates = sorted({p.resolve() for p in (a.budget_root or [BASE, work])}, key=lambda p: len(p.parts))
    roots = []
    for p in candidates:
        if not any(p.is_relative_to(parent) for parent in roots): roots.append(p)
    from arithmetic import run
    report = run(a.family, work, a.scope, a.workers, a.sample, a.max_seconds,
                 a.max_batches, roots, a.max_bytes)
    if report['status'] not in ('COMPLETE', 'PAUSED'):
        raise SystemExit(2)
