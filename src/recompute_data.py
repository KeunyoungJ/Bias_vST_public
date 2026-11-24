# 터미널 옵션을 읽어 한 family의 재계산을 시작한다.
# public_release/에서 소규모로 실행하는 예
#   python src/recompute_data.py --family conductor --scope smoke
#
# --family       conductor(도체) 또는 height(높이) 기준의 곡선 집합을 고른다. 필수다.
# --scope        smoke는 소규모 시험, full은 전체 계산이다. 기본은 smoke다.
# --sample       smoke에서 각 shell의 CM/non-CM 그룹별 표본 수다. 기본은 3이다.
# --workers      병렬 계산에 쓸 프로세스 수다. 기본은 1이다.
# --work-dir     계수 DB와 실행 기록을 둘 폴더다. 기본은 work/{scope}_{family}/다.
# --max-seconds  이번 실행의 시간 한도(초)다. 기본값 0은 시간 제한을 해제한다.
# --max-batches  이번 실행에서 저장할 batch 수의 한도다. 기본값 0은 개수 제한을 해제한다.
# --budget-root  저장량을 합산할 폴더다. 여러 번 지정할 수 있다.
# --max-bytes    위 폴더들의 저장량 한도(바이트)다. 기본은 10 GiB다.
# --budget-root를 생략하면 public_release/와 작업 폴더를 기준으로 잡는다.
# 한 폴더가 다른 폴더 안에 있으면 상위 폴더의 사용량에 이미 포함된다.
#
# 계산을 따라 읽으려면 arithmetic.py의 run()으로 넘어가면 된다.
# 곡선 목록을 읽는 부분과 bin 격자는 bvst_data.py의 load_family()와 grid()에 있다.

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
