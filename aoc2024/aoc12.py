from pathlib import Path
import time
from rich import print
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table


from aoc2024.get_input import get_input

test_input = """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])


Point = tuple[int, int]

Area = set[Point]


class Garden:
    def __init__(self, bla: str) -> None:
        self._rows: list[list[str]] = list(map(list, bla.strip().splitlines()))

        blank_row = ["."] * len(self._rows[0]) * 2
        grid = (
            [blank_row + [".", ".", "."]]
            + [
                [".", "."] + row + ["."]
                for rows in zip(
                    [blank_row] * len(self._rows),
                    [
                        [r for t in zip(row, ["."] * len(row)) for r in t]
                        for row in self._rows
                    ],
                )
                for row in rows
            ]
            + [blank_row + [".", ".", "."]] * 2
        )
        self._shape: Point = len(grid), len(grid[0])

        self._grid: list[list[str]] = grid
        self._areas: list[tuple[str, Area | frozenset[Point]]] = []
        self._fences: dict[tuple[str, Area], list[Point]] = dict()
        self._current: Point | None = None
        self._fence: dict[Point, str] = dict()
        self._discarded: set[Point] = set()

    @property
    def areas(self):
        return self._areas

    @property
    def fences(self):
        bort = [(m, len(area), len(fence)) for (m, area), fence in self._fences.items()]
        return bort

    @property
    def cost(self):
        return sum(a * f for _, a, f in self.fences)

    @property
    def cost_discount(self):
        def dist(p1: Point, p2: Point):
            return abs(p1[0] - p2[0]) ** 2 + abs(p1[1] - p2[1]) ** 2

        cost: list[tuple[str, int]] = []
        for (m, area), fence in self._fences.items():
            start = sorted(fence)[0]
            horst: set[Point] = set()
            edges: set[Point] = set()
            current = start
            while current not in horst:
                ii, jj = current
                next_candidates = sorted(
                    (
                        (ii + bla, jj + blub)
                        for bla, blub in [
                            (-2, 0),
                            (-1, 1),
                            (0, 2),
                            (1, 1),
                            (2, 0),
                            (1, -1),
                            (0, -2),
                            (-1, -1),
                        ]
                        if (ii + bla, jj + blub) in fence
                        and (ii + bla // 2, jj + bla // 2) not in area
                        and (ii + bla, jj + blub) not in horst
                    ),
                    key=lambda x: dist(current, x),
                )
                next_pos = next(
                    iter(next_candidates),
                    None,
                )
                if next_pos is None:
                    break
                if next_pos[0] == ii or next_pos[1] == jj:
                    self._discarded.add(next_pos)
                else:
                    edges.add(next_pos)
                print(
                    # f"m: {m}, current: {current}, next cand: {next_candidates},\nnext: {next_pos}, edges: {edges}"
                    f"m: {m}, current: {current}, next: {next_pos}, edges: {edges}, {len(edges)}"
                )
                current = next_pos
                horst.add(current)
            cost.append((m, len(area) * len(edges)))
        return cost

    def __rich__(self):
        def render_pos(ii: int, jj: int):
            style = "black"
            m = self._grid[ii][jj]
            if not m == ".":
                for idx, (mark, area) in enumerate(self._areas):
                    if m == mark and (ii, jj) in area:
                        style = f"color({idx + 128})"
                        break
                bla = m
            elif (ii, jj) in self._fence:
                bla = self._fence[(ii, jj)]
                if (ii, jj) in self._discarded:
                    style = "red"
                else:
                    style = "white"
            else:
                bla = m

            if (ii, jj) == self._current:
                style = f"{style} on red"
            return f"[{style}]{bla}[/]"

        table = Table.grid()
        table.add_row(
            Panel(
                "\n".join(
                    "".join(render_pos(ii, jj) for jj, _ in enumerate(row))
                    for ii, row in enumerate(self._grid)
                ),
                title="Map",
            ),
            Panel(
                # Pretty((self.cost, self.cost_discount)),
                Pretty((self.cost)),
                # f"{self.cost}",
                title="Cost",
            ),
        )
        return table

    def build_fence(self, marker: str, area: Area, slow: bool = False):
        bort = [
            (ii + bla, jj + blub)
            for ii, jj in sorted(area)
            for bla, blub in [(-1, 0), (0, 1), (1, 0), (0, -1)]
        ]
        bort = [
            (ii, jj)
            for ii, jj in bort
            if not (
                self._grid[ii][jj - 1] == marker and self._grid[ii][jj + 1] == marker
            )
            and not (
                self._grid[ii - 1][jj] == marker and self._grid[ii + 1][jj] == marker
            )
        ]
        for ii, jj in bort:
            self._fence[(ii, jj)] = "+"
            self._fences[(marker, area)] = bort
            if slow:
                time.sleep(0.02)
        time.sleep(0.05)

    def explore(self, slow: bool = False):
        left = {
            (ii, jj)
            for ii, row in enumerate(self._grid)
            for jj, c in enumerate(row)
            if not c == "."
        }

        s_ii, s_jj = self._shape

        def grab_area(
            marker: str,
            pos: Point,
            bort: Area,
        ):
            ii, jj = pos
            neighbours = {
                (ii + bla, jj + blub)
                for bla, blub in [(-2, 0), (0, 2), (2, 0), (0, -2)]
                if 0 <= ii + bla < s_ii
                and 0 <= jj + blub < s_jj
                and self._grid[ii + bla][jj + blub] == marker
            }
            for n in neighbours - bort:
                bort.add(n)
                if slow:
                    time.sleep(0.005)
                _ = grab_area(marker, n, bort)

        while left:
            ii, jj = left.pop()
            m = self._grid[ii][jj]
            a = {(ii, jj)}
            self._areas.append((m, a))
            grab_area(m, (ii, jj), a)
            self._areas.remove((m, a))
            self._areas.append((m, frozenset(sorted(a))))
            left -= a


def part1(test: bool = False, discount: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    g = Garden(input)
    with Live(g, refresh_per_second=5):
        g.explore(slow=test)
        for m, a in g.areas:
            if m == "I":
                g.build_fence(m, a, slow=test)
    print(g.cost_discount)
    print(g)
    return g.cost


def part2(test: bool = False):
    return part1(test, discount=True)
