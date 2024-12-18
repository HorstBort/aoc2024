from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys
import time
from typing import Self, final, override

from rich import print

from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress


from aoc2024.get_input import get_input

test_input = """
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
""".strip()

test_input_2 = """
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################
"""

# test_input_2 = """
# #######
# # # #E#
# #   # #
# # # # #
# # #   #
# # ### #
# #S    #
# ########
# """


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


dir_str = {
    Direction.UP: "^",
    Direction.RIGHT: ">",
    Direction.DOWN: "v",
    Direction.LEFT: "<",
}


@final
class PathNode:
    def __init__(
        self,
        parent: Self | None,
        pos: Point,
        direction: Direction,
        children: list[Self],
    ) -> None:
        self.parent = parent
        self.pos = pos
        self.dir = direction
        self.children = children
        if parent is None:
            self._path = [self]
            self._pos_path = [pos]
            self._cost = 0
        else:
            self._path = parent.path + [self]
            self._pos_path = parent.pos_path + [pos]
            if direction == parent.dir:
                self._cost = 1 + parent.cost
            else:
                self._cost = 1001 + parent.cost

    @property
    def path(self) -> list[Self]:
        return self._path

    @property
    def pos_path(self) -> list[Point]:
        return self._pos_path

    @property
    def flat(self) -> list[Self]:
        return [self] + [cch for ch in self.children for cch in ch.flat]

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:<{self.pos}, {self.dir}: {self.children}>"

    @property
    def cost(self) -> int:
        return self._cost

    @override
    def __hash__(self) -> int:
        return hash((self.pos, self.dir))


@dataclass
class Maze:
    walls: set[Point]
    start: Point
    finish: Point
    shape: Point
    current: PathNode | None = None
    depth: int = 0
    best: int | None = None
    paths: list[PathNode] | None = None
    dead_ends: set[Point] | None = None
    seen: dict[tuple[Point, Direction], int] | None = None
    seen_pos: set[Point] | None = None

    @classmethod
    def from_str(cls, s: str):
        grid = list(map(list, s.strip().splitlines()))
        walls = {
            (ii, jj)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "#"
        }
        start = next(
            (ii, jj)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "S"
        )
        finish = next(
            (ii, jj)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "E"
        )
        return Maze(
            walls,
            start,
            finish,
            (len(grid), len(grid[0])),
        )

    def find_dead_ends(self):
        dead_ends = {
            (ii, jj)
            for ii in range(1, self.shape[0] - 1)
            for jj in range(1, self.shape[1] - 1)
            if (ii, jj) not in self.walls
            and (
                {(ii - 1, jj), (ii, jj - 1), (ii, jj + 1)} < self.walls
                or {(ii, jj + 1), (ii - 1, jj), (ii + 1, jj)} < self.walls
                or {(ii + 1, jj), (ii, jj - 1), (ii, jj + 1)} < self.walls
                or {(ii, jj - 1), (ii - 1, jj), (ii + 1, jj)} < self.walls
            )
        }
        return dead_ends - {self.start, self.finish}

    def fill_dead_corridor(self, de: Point):
        dead_corridor: set[Point] = {de}
        np = {p for p, _ in self.next_positions(de, Direction.UP)}
        while len(np) == 1:
            for nn in np:
                np = (
                    {p for p, _ in self.next_positions(nn, Direction.UP)}
                    - dead_corridor
                    - {self.finish, self.start}
                )
                if len(np) == 1:
                    dead_corridor.add(nn)
        if self.dead_ends is None:
            self.dead_ends = set()
        self.dead_ends = self.dead_ends | dead_corridor

    def next_positions(self, pos: Point, dir: Direction):
        bort = [
            ((0, 1), Direction.RIGHT),
            ((1, 0), Direction.DOWN),
            ((0, -1), Direction.LEFT),
            ((-1, 0), Direction.UP),
        ]
        for _ in range(dir.value):
            bort.append(bort.pop(0))
        y, x = pos
        return [
            ((ii + y, jj + x), d)
            for (ii, jj), d in reversed(bort)
            if (ii + y, jj + x) not in self.walls
        ]

    def step(
        self,
        parent: PathNode,
        test: bool = False,
        depth: int = 0,
    ):
        self.depth = depth
        self.current = parent
        if self.paths is None:
            self.paths = []
        if self.dead_ends is None:
            self.dead_ends = set()
        if self.seen is None:
            self.seen = dict()
        if self.seen_pos is None:
            self.seen_pos = set()
        key = (parent.pos, parent.dir)
        if key in self.seen and self.seen[key] < parent.cost:
            return
        self.seen[key] = parent.cost
        self.seen_pos.add(parent.pos)
        if parent.pos == self.finish:
            self.best = (
                parent.cost if self.best is None else min(self.best, parent.cost)
            )
            self.paths.append(parent)
            self.paths.sort(key=lambda x: x.cost)
            # print("Bort")
            # print(Panel(f"{self.best}, {[p.cost for p in self.paths]}"))
            return

        next_pos = self.next_positions(parent.pos, parent.dir)
        next_pos = [
            (p, d)
            for p, d in next_pos
            if p not in parent.pos_path and p not in self.dead_ends
        ]
        if test or parent.pos == self.finish or len(parent.path) % 100 == 0:
            time.sleep(0.1)
        children = parent.children
        for p, d in next_pos:
            node = PathNode(parent, p, d, [])
            if self.best is None or node.cost <= self.best:
                self.step(node, test, depth=depth + 1)
                children.append(node)

    def __rich__(self):
        prog = Progress()
        lay = Layout()
        lay.split_column(Layout(Panel(prog), size=4), Layout(name="bort"))
        lay["bort"].split_row(
            Layout(self.render_path(), name="wh"),
            Layout(Panel(""), name="move", size=50),
        )
        if self.current is not None:
            dist = abs(self.finish[0] - self.current.pos[0]) + abs(
                self.finish[1] - self.current.pos[1]
            )
        else:
            dist = ""
        lay["move"].update(
            Group(
                Panel(
                    f"finish: {self.finish}\ndist: {dist}\nbest: {self.best}\ncurrent: {self.current.cost if self.current is not None else None}\ncost: {[p.cost for p in self.paths] if self.paths is not None else []}",
                    title="Results",
                ),
                Panel(f"depth: {self.depth}", title="Status"),
                # Panel(
                #     f"seen: {len(self.seen) if self.seen is not None else 0}",
                #     title="Seen",
                # ),
                Panel(
                    (
                        f"pos: {self.current.pos if self.current is not None else None}\n"
                        f"current: {self.current.cost if self.current is not None else None}\n"
                        # f"seen: {self.seen[self.current] if self.current is not None  and self.seen is not None else None}\n"
                        # f"Arsch: {[v for v in self.seen.keys() if v.pos == (7, 15)] if self.seen is not None else None}\n"
                    ),
                    title="Seen cost",
                ),
                # Panel(
                #     Pretty(
                #         sorted(self.dead_ends) if self.dead_ends is not None else ""
                #     ),
                #     title="dead",
                # ),
            )
        )
        return lay

    def render_path(self):
        current = self.current

        def render_pos(ii: int, jj: int):
            if (ii, jj) in self.walls:
                return "[bright_black]#[/]"
            elif (ii, jj) == self.start:
                return "[yellow]S[/]"
            elif self.dead_ends is not None and (ii, jj) in self.dead_ends:
                return "[red]x[/]"
            elif path is not None and current is not None and (ii, jj) in path:
                if (ii, jj) == current.pos:
                    return ":deer:"
                else:
                    col = "magenta"
                d = dir_str[path[(ii, jj)]]
                return f"[{col}]{d}[/]"
            elif (ii, jj) == self.finish:
                return "[green]E[/]"
            elif (
                self.paths is not None
                and self.paths
                and any((ii, jj) in bort.pos_path for bort in self.paths)
            ):
                for nn, bort in enumerate(self.paths):
                    pos = bort.pos_path
                    if (ii, jj) in pos:
                        c = f"color({nn + 153})"
                        # c = "cyan3"
                        return f"[{c}]¤[/]"
            elif self.seen_pos is not None and (ii, jj) in self.seen_pos:
                return "[blue]+[/]"

            return "."

        if current is None:
            path = None
            roi_i = 0, self.shape[0]
            roi_j = 0, self.shape[1]
        else:
            w_x = 40
            w_y = 20
            w_x = self.shape[1]
            w_y = self.shape[0]
            path = {n.pos: n.dir for n in current.path}
            top = max(0, min(current.pos[0] - w_y // 2, self.shape[0] - w_y - 1))
            roi_i = top, min(self.shape[0], top + w_y)
            left = max(0, min(current.pos[1] - w_x // 2, self.shape[1] - w_x - 1))
            roi_j = left, min(left + w_x, self.shape[1])
            # raise Exception()
        bort = [[render_pos(ii, jj) for jj in range(*roi_j)] for ii in range(*roi_i)]
        s = "\n".join(map("".join, bort))
        return Panel(s)


class Rotation(Enum):
    LEFT = -1
    RIGHT = 1


def part1(test: bool = False, part2: bool = False):
    if test:
        if not part2:
            input = test_input_2
        else:
            input = test_input_2
    else:
        input = get_input(DAY)

    maze = Maze.from_str(input)

    sys.setrecursionlimit(10000)
    # lay["move"].split_column(
    #     Layout(name="ii", size=3),
    #     Layout(name="mv"),
    # )
    #

    start = PathNode(None, maze.start, Direction.RIGHT, [])

    with Live(maze, refresh_per_second=10 if test else 1):
        dead_ends = maze.find_dead_ends()
        maze.dead_ends = dead_ends
        time.sleep(0.1)
        for de in dead_ends:
            maze.fill_dead_corridor(de)
            if test:
                time.sleep(0.1)
        maze.step(start, test)
        maze.current = None
        time.sleep(5)
    # maze.step(start, lay["wh"], lay["move"], test)

    paths = [p for p in start.flat if p.pos == maze.finish]
    cost_min = min(p.cost for p in paths)
    if not part2:
        return cost_min
    else:
        return len(
            {p for path in paths if path.cost == cost_min for p in path.pos_path}
        )


def part2(test: bool = False):
    return part1(test, part2=True)
