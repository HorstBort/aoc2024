import importlib
from types import ModuleType

import keyring

import pyperclip

import typer

from rich.prompt import Prompt

days = range(1, 26)

mods: list[ModuleType] = []
for ii in days:
    try:
        m = importlib.import_module(f"aoc2024.aoc{ii}")
    except ModuleNotFoundError:
        pass
    else:
        mods.append(m)


app = typer.Typer()


@app.command()
def run(day: int, part: int, test: bool = False):
    cookie = keyring.get_password("aoc2024", "session_cookie")
    if cookie is None:
        cookie = Prompt.ask(
            "Enter session cookie to automatically download input files"
        )
        if cookie.strip():
            keyring.set_password("aoc2024", "session_cookie", cookie)

    m = mods[day - 1]
    if part == 1:
        res = m.part1(test)  # pyright: ignore[reportAny]
    elif part == 2:
        res = m.part2(test)  # pyright: ignore[reportAny]
    else:
        print("1...2...many, right?")
        raise typer.Exit()

    print(f"Result for day {day}, part {part}: {res}")
    if not test:
        pyperclip.copy(f"{res}")  # pyright: ignore[reportUnknownMemberType]
        print("(copied to clipboard)")


@app.callback(invoke_without_command=True)
def main():
    pass


if __name__ == "__main__":
    app()
