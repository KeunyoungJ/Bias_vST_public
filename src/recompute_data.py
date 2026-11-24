"""Recompute one elliptic curve family, including CM curves (default: smoke run)."""

import argparse
from pathlib import Path

from bvst_data import BASE


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', choices=['conductor', 'height'], required=True)
    parser.add_argument('--scope', choices=['smoke', 'full'], default='smoke',
                        help='compute a small test sample (default) or the entire family')
    parser.add_argument('--family-dir', type=Path, default=BASE/'data',
                        help='directory containing the frozen family input (default: bundled data/)')
    parser.add_argument('--work-dir', type=Path,
                        help='checkpoint and log directory (default: work/{scope}_{family}/)')
    parser.add_argument('--output-dir', type=Path,
                        help='NPZ output directory (default: work/reproduced/data/ for full runs, '
                             'the checkpoint directory for smoke runs)')
    parser.add_argument('--workers', type=int, default=1, help='worker processes (default: 1)')
    parser.add_argument('--sample', type=int, default=3,
                        help='deterministic sample size for each CM/non-CM group per shell (default: 3)')
    parser.add_argument('--max-seconds', type=float, default=0, help='time limit in seconds; 0 for no limit')
    parser.add_argument('--max-batches', type=int, default=0, help='new batch limit; 0 for no limit')
    parser.add_argument('--budget-root', type=Path, action='append', default=[],
                        help='directory counted toward the storage budget; repeat as needed')
    parser.add_argument('--max-bytes', type=int, default=10*1024**3,
                        help='combined storage budget in bytes (default: 10 GiB)')
    args = parser.parse_args(argv)
    if args.workers < 1 or args.sample < 2:
        parser.error('--workers must be at least 1 and --sample at least 2')

    work = args.work_dir or BASE/'work'/f'{args.scope}_{args.family}'
    output = args.output_dir or (BASE/'work/reproduced/data' if args.scope == 'full' else work)
    # Count the output directory too when using the default storage budget roots.
    candidates = sorted({p.resolve() for p in (args.budget_root or [BASE, work, output])},
                        key=lambda p: len(p.parts))
    roots = []
    for path in candidates:
        if not any(path.is_relative_to(parent) for parent in roots):
            roots.append(path)
    from arithmetic import run
    report = run(args.family, work, args.scope, args.workers, args.sample, args.max_seconds,
                 args.max_batches, roots, args.max_bytes,
                 family_dir=args.family_dir, output_dir=output)
    if report['status'] not in ('COMPLETE', 'PAUSED'):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
