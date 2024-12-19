from pathlib import Path
import time
from typing import final

from rich import print

from rich.live import Live


from aoc2024.get_input import get_input

test_input = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@final
class Grid:
    def __init__(self, size: int) -> None:
        self._size = size
        self._corrupt = []
        self._seen: dict[Point, int] = dict()
        self._current: Point = (0, 0)
        self._exit = (self._size - 1, self._size - 1)

    @property
    def corrupt(self):
        return self._corrupt

    @corrupt.setter
    def corrupt(self, value: list[Point]):
        self._corrupt = value

    def __rich__(self):
        def extracted_method(p: Point):
            if p in self.corrupt:
                return "#"
            elif p == self._current:
                return "[green]x[/]"
            elif p in self._seen:
                return "[red].[/]"
            else:
                return "."

        bla = [
            [extracted_method((ii, jj)) for jj in range(self._size)]
            for ii in range(self._size)
        ]
        return "\n".join(map("".join, bla))

    def walk(self, pos: Point | None = None, depth: int = 0, slow: bool = False):
        if pos is None:
            pos = (0, 0)

        self._current = pos
        self._seen[pos] = (
            depth if pos not in self._seen else min(depth, self._seen[pos])
        )
        if pos == self._exit:
            return
        if slow:
            time.sleep(0.1)
        y, x = pos
        next = [
            (y + bla, x + blub)
            for bla, blub in [(1, 0), (0, 1), (0, -1), (-1, 0)]
            if 0 <= y + bla < self._size
            and 0 <= x + blub < self._size
            and (
                (y + bla, x + blub) not in self._seen
                or self._seen[(y + bla, x + blub)] > depth + 1
            )
            and (y + bla, x + blub) not in self.corrupt
        ]
        for n in next:
            self.walk(n, depth + 1, slow)

    @property
    def min(self):
        return self._seen[self._exit]


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    def line_to_coord(line: str):
        x, y = line.split(",")
        return int(y), int(x)

    corrupt: list[Point] = list(
        map(
            line_to_coord,
            input.strip().splitlines(),
        )
    )
    grid = Grid(7 if test else 71)
    with Live(grid):
        grid.corrupt = corrupt[:12] if test else corrupt[:1024]
        grid.walk(slow=test)

    return grid.min


def part2(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    return part1(test)
