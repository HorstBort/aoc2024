from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from rich import print

from rich.panel import Panel


from aoc2024.get_input import get_input

test_input = """
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
""".strip()

test_input_2 = test_input

DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@dataclass
class Warehouse:
    grid: list[list[str]]
    robot: Point

    def move_robot(self, direction: Literal["^", ">", "v", "<"]):
        ii, jj = self.robot
        match direction:
            case "^":
                pass
            case ">":
                pass
            case "v":
                pass
            case "<":
                path = self.grid[self.robot[0]][: self.robot[1] - 1]

    @classmethod
    def from_str(cls, s: str):
        grid = list(map(list, s.strip().splitlines()))
        robot = next(
            (ii, jj)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "@"
        )
        return Warehouse(grid, robot)

    def __rich__(self):
        s = "\n".join(map("".join, self.grid))
        return Panel(s)


def part1(test: bool = False, part2: bool = False):
    if test:
        if not part2:
            input = test_input
        else:
            input = test_input_2
    else:
        input = get_input(DAY)

    warehouse, movements = input.split("\n\n")
    wh = Warehouse.from_str(warehouse)
    print(wh)
    return


def part2(test: bool = False):
    return part1(test, part2=True)
