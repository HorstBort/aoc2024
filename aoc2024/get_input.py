import requests
from pathlib import Path


def get_input(day: int):
    p = Path(f"res/{day}.txt")
    p.parent.mkdir(exist_ok=True)

    if not p.is_file():
        r = requests.get(f"https://adventofcode.com/2024/day/{day}/input")
        input: str = r.content.decode()
        _ = p.write_text(input)
    else:
        input = p.read_text()
    return input
