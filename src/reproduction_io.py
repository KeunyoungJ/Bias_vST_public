# 계산·그림·표 코드가 공통으로 사용하는 출력 저장 함수다.
# save_outputs(directory, outputs)는 출력 폴더와 {파일명: 저장할 바이트}를 받는다.
#
# 먼저 모든 대상의 기존 내용을 검사한다. 하나라도 새 바이트와 다르면
# FileExistsError를 발생시켜 이번 호출의 파일 쓰기를 시작하기 전에 멈춘다.
# 내용이 같은 기존 파일은 재사용하고, 아직 없는 파일을 쓴 뒤 각 경로를 반환한다.
#
# 넘겨주는 바이트가 어떻게 만들어지는지 보려면 산출물별 호출부를 보면 된다.
# NPZ는 arithmetic.py, PNG/PDF는 make_figures.py, CSV는 make_tables.py에서 넘긴다.

from pathlib import Path


def save_outputs(directory, outputs):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, raw in outputs.items():
        p = directory/name
        if p.exists() and p.read_bytes() != raw:
            raise FileExistsError(f'Existing result differs: {p}')
    for name, raw in outputs.items():
        p = directory/name
        if not p.exists():
            p.write_bytes(raw)
    return [str(directory/name) for name in outputs]
