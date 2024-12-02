import importlib
from types import ModuleType

import typer


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
    m = mods[day - 1]
    if part == 1:
        print(m.part1(test))  # pyright: ignore[reportAny]
    elif part == 2:
        print(m.part2(test))  # pyright: ignore[reportAny]


@app.callback(invoke_without_command=True)
def main():
    pass


if __name__ == "__main__":
    app()
