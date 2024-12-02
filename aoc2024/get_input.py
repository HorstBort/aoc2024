import keyring
import requests
from pathlib import Path


def get_input(day: int):
    p = Path(f"res/{day}.txt")
    p.parent.mkdir(exist_ok=True)

    if not p.is_file():
        cookie = keyring.get_password("aoc2024", "session_cookie")
        if cookie is None:
            raise ValueError(
                f"Cannot download input for day {day}, session_cookie not available."
            )
        cookies = {"session": cookie}
        r = requests.get(
            f"https://adventofcode.com/2024/day/{day}/input", cookies=cookies
        )
        input: str = r.content.decode()
        _ = p.write_text(input)
    else:
        input = p.read_text()
    return input
