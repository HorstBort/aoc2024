import time
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Self

from loguru import logger
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from typing_extensions import override

from aoc2024.get_input import get_input


test_input = """
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
""".strip()

test_input_2 = """
""".strip()


@dataclass
class Point:
    x: int
    y: int

    @override
    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: Self):
        return Point(self.x + other.x, self.y + other.y)

    def __lt__(self, other: Self):
        return (self.x, self.y) < (other.x, other.y)


@dataclass
class Array:
    rows: list[list[str]]

    def __iter__(self) -> Iterator[list[str]]:
        yield from self.rows

    def __getitem__(self, idx: int):
        return self.rows[idx]

    @property
    def shape(self):
        return len(self.rows), len(self.rows[0])

    def contains(self, p: Point):
        s_y, s_x = self.shape
        return -1 < p.x < s_x and -1 < p.y < s_y

    def blocked(self, p: Point):
        return self.rows[p.y][p.x] == "#"


class Direction(Enum):
    DOWN = Point(0, 1)
    UP = Point(0, -1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)


str_to_dir = {
    "^": Direction.UP,
    "<": Direction.LEFT,
    ">": Direction.RIGHT,
    "v": Direction.DOWN,
}

dir_to_str = {v: k for k, v in str_to_dir.items()}


class Guard:
    def __init__(
        self,
        array: Array,
        pos_initial: Point,
        dir_initial: Direction,
        trace: bool = True,
    ) -> None:
        self._arr: Array = array
        self._columns: Array = Array(list(zip(*array.rows)))
        self._pos: Point = pos_initial
        self._dir: Direction = dir_initial
        self._visited: set[Point] = {pos_initial}
        self._loop_detector: set[tuple[Point, Direction]] = {(pos_initial, dir_initial)}
        self._stuck_in_loop: bool = False
        self._trace: bool = trace

    def step(self, sprint: bool = False):
        pos = self._pos
        dir = self._dir
        pos_next = pos + dir.value
        while self._arr.contains(pos_next) and self._arr.blocked(pos_next):
            # logger.debug("Turning: pos: {}, dir: {}", pos, dir)
            match dir:
                case Direction.UP:
                    dir = Direction.RIGHT
                case Direction.RIGHT:
                    dir = Direction.DOWN
                case Direction.DOWN:
                    dir = Direction.LEFT
                case Direction.LEFT:
                    dir = Direction.UP
            pos_next = pos + dir.value
        # logger.debug("Moved: pos: {}, dir: {}", pos_next, dir)
        if sprint:
            pos_next = self.next_pos(pos_next, dir)
            if self._trace:
                match dir:
                    case Direction.LEFT | Direction.RIGHT:
                        visited = {
                            Point(ii, pos.y)
                            for ii in range(
                                min(pos.x, pos_next.x), max(pos.x, pos_next.x) + 1
                            )
                        }
                    case Direction.UP | Direction.DOWN:
                        visited = {
                            Point(pos.x, ii)
                            for ii in range(
                                min(pos.y, pos_next.y), max(pos.y, pos_next.y) + 1
                            )
                        }
                self._visited |= {p for p in visited if self._arr.contains(p)}

        elif self._trace:
            visited: set[Point] = {pos_next}
            self._visited |= {p for p in visited if self._arr.contains(p)}
        # logger.debug("Moved: pos: {}, dir: {}", pos_next, dir)
        self._dir = dir
        self._pos = pos_next
        if not self.exited:
            if (pos_next, dir) in self._loop_detector:
                self._stuck_in_loop = True
            else:
                self._loop_detector.add((pos_next, dir))

    def next_pos(self, pos: Point, dir: Direction):
        if not self._arr.contains(pos):
            return pos
        col = self._columns[pos.x]
        row = self._arr[pos.y]
        match dir:
            case Direction.UP:
                try:
                    next_obs = len(col) - col[::-1].index("#", len(col) - pos.y)
                except ValueError:
                    return Point(pos.x, 0)
                else:
                    return Point(pos.x, next_obs)
            case Direction.RIGHT:
                try:
                    next_obs = row.index("#", pos.x)
                except ValueError:
                    return Point(len(row), pos.y)
                else:
                    return Point(next_obs - 1, pos.y)
            case Direction.DOWN:
                try:
                    next_obs = col.index("#", pos.y)
                except ValueError:
                    return Point(pos.x, len(col))
                else:
                    return Point(pos.x, next_obs - 1)
            case Direction.LEFT:
                try:
                    next_obs = len(row) - row[::-1].index("#", len(row) - pos.x)
                except ValueError:
                    return Point(0, pos.y)
                else:
                    return Point(next_obs, pos.y)

    @property
    def pos(self):
        return self._pos

    @property
    def dir(self):
        return self._dir

    @property
    def nr_pos_visited(self):
        return len(self._visited)

    @property
    def exited(self):
        return not self._arr.contains(self._pos)

    @property
    def stuck_in_loop(self):
        return self._stuck_in_loop

    @property
    def visited(self):
        return self._visited

    def __rich__(self):
        out: list[list[str]] = []
        for r, row in enumerate(self._arr):
            r_out: list[str] = []
            for c, v in enumerate(row):
                p = Point(c, r)
                if p == self._pos:
                    s = dir_to_str[self._dir]
                elif p in self._visited:
                    s = "X"
                else:
                    s = v
                r_out.append(s)
            out.append(r_out)
        return "\n".join("".join(r) for r in out)


def part1(test: bool = False, put_obstacles: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(6)

    arr = Array(list(map(list, input.splitlines())))

    dir_initial, pos_initial = [
        (str_to_dir[v], Point(c, r))
        for r, row in enumerate(arr)
        for c, v in enumerate(row)
        if v in str_to_dir
    ][0]

    g = Guard(arr, pos_initial, dir_initial)
    # print(dir_initial, pos_initial)
    lay = Layout(name="root")
    lay.split(
        Layout(name="progress", size=3),
        Layout(name="obs", size=3),
        Layout(name="main"),
        Layout(name="log"),
    )
    log_table = Table(show_lines=False, show_edge=False)
    log_table.add_column("Logging")

    messages: deque[str] = deque(maxlen=20)

    def _append_log(msg: str):
        messages.append(msg)
        lay["log"].update(Panel("".join(messages), title="Logging"))

    logger.remove()
    if test:
        _ = logger.add(_append_log)

    lay["main"].update(Panel(g, title="Map"))
    if not put_obstacles:
        if test:
            with Live(lay, refresh_per_second=10):
                while not g.exited:
                    lay["main"].update(Panel(g, title="Map"))
                    g.step(sprint=False)
                    time.sleep(0.01)
        else:
            while not g.exited:
                g.step()
        return g.nr_pos_visited
    else:
        obstacles: set[Point] = set()
        lay["obs"].split_row(Layout(name="obs_cur"), Layout(name="obs_total"))
        lay["main"].split_row(Layout(name="map"), Layout(name="obs_table"))

        # Initial run to narrow down possible locations
        while not g.exited:
            g.step()

        possible_obstacles = g.visited - {pos_initial}
        p = Progress(
            SpinnerColumn(),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        t_total = p.add_task("Total", total=len(possible_obstacles))

        lay["progress"].update(Panel(p, title="Progress"))
        lay["map"].update(Panel(g))
        table_obs = Table()
        table_obs.add_column("Valid obstacles")
        lay["obs_table"].update(Panel(table_obs))

        with Live(lay, refresh_per_second=10, screen=False):
            for obs in possible_obstacles:
                lay["obs_cur"].update(Panel(str(obs), title="Current obs"))
                lay["obs_total"].update(
                    Panel(str(len(obstacles)), title="Number of valid obs")
                )
                p.advance(t_total, 1)
                v_orig = arr[obs.y][obs.x]
                arr[obs.y][obs.x] = "#"
                g = Guard(arr, pos_initial, dir_initial, trace=False)
                lay["map"].update(Panel(g))
                while not g.exited and not g.stuck_in_loop:
                    g.step(sprint=True)
                    if test:
                        lay["map"].update(Panel(g))
                        # time.sleep(0.01)
                if g.stuck_in_loop:
                    obstacles.add(obs)
                    table_obs.add_row(str(obs))
                arr[obs.y][obs.x] = v_orig
        return len(obstacles)

    # print(g.pos, g.dir, g)


def part2(test: bool = False):
    return part1(test, True)
