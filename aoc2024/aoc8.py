from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
import itertools
from typing import Self
from typing_extensions import override

from rich import print

from aoc2024.get_input import get_input

test_input = """
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
""".strip()

test_input_2 = """
T.........
...T......
.T........
..........
..........
..........
..........
..........
..........
..........
""".strip()


def add(a: int, b: int):
    return a + b


def mul(a: int, b: int):
    return a * b


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other: Self):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self):
        return Point(self.x - other.x, self.y - other.y)

    def __lt__(self, other: Self):
        return self.x + self.y < other.x + other.y

    @override
    def __hash__(self) -> int:
        return hash((self.x, self.y))


@dataclass
class Grid:
    rows: Sequence[str]
    resonant: bool = False

    def __post_init__(self):
        self._shape: tuple[int, int] = (  # pyright: ignore[reportUninitializedInstanceVariable]
            len(self.rows),
            len(self.rows[0]),
        )

    @property
    def shape(self):
        return self._shape

    @property
    def antennas(self):
        antennas = {
            (y, x): v
            for y, row in enumerate(self.rows)
            for x, v in enumerate(row)
            if not v == "."
        }
        return {
            a: {Point(x, y) for (y, x), v in antennas.items() if v == a}
            for a in set(antennas.values())
        }

    @property
    def antenna_points(self):
        return {p for points in self.antennas.values() for p in points}

    @property
    def nodes_by_antenna(self):
        antennas = self.antennas
        nodes: dict[str, set[Point]] = defaultdict(set)
        # print(antennas)
        for a, points in antennas.items():
            for p1, p2 in map(sorted, itertools.combinations(points, 2)):
                node1 = p1 + (p1 - p2)
                node2 = p2 + (p2 - p1)
                while self.contains(node1):
                    nodes[a].add(node1)
                    if not self.resonant:
                        break
                    node1 = node1 + (p1 - p2)
                while self.contains(node2):
                    nodes[a].add(node2)
                    if not self.resonant:
                        break
                    node2 = node2 + (p2 - p1)
                if self.resonant:
                    node1 = p1 - (p1 - p2)
                    node2 = p2 - (p2 - p1)
                    while self.contains(node1):
                        nodes[a].add(node1)
                        if not self.resonant:
                            break
                        node1 = node1 - (p1 - p2)
                    while self.contains(node2):
                        nodes[a].add(node2)
                        if not self.resonant:
                            break
                        node2 = node2 - (p2 - p1)
        return nodes

    @property
    def nodes(self):
        return {p for nodes in self.nodes_by_antenna.values() for p in nodes}

    def contains(self, p: Point):
        s_y, s_x = self.shape
        return 0 <= p.x < s_x and 0 <= p.y < s_y

    def __rich__(self):
        colors = {".": "grey", "#": "red"}
        nodes = {(p.x, p.y) for node in self.nodes_by_antenna.values() for p in node}
        with_nodes = [
            ["#" if c == "." and (x, y) in nodes else c for x, c in enumerate(row)]
            for y, row in enumerate(self.rows)
        ]
        return "\n".join(
            "".join(f"[{colors[c]}]{c}[/]" if c in colors else c for c in row)
            for row in with_nodes
        )


def part1(test: bool = False, part2: bool = False):
    if test:
        input = test_input if not part2 else test_input_2
    else:
        input = get_input(8)

    grid = Grid(input.splitlines(), part2)
    print(grid)
    # print(grid.antennas)
    # print(grid.nodes)
    return len(grid.nodes)


def part2(test: bool = False):
    return part1(test, True)
