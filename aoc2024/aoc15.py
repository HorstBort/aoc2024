from dataclasses import dataclass
from pathlib import Path
import time
from typing import Literal


from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress


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

# test_input = """
# ########
# #..O.O.#
# ##@.O..#
# #...O..#
# #.#.O..#
# #...O..#
# #......#
# ########
#
# <^^>>>vv<v>>v<<
# """

test_input_2 = test_input

DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@dataclass
class Warehouse:
    grid: list[list[str]]
    robot: Point

    def move_robot(self, direction: Literal["^", ">", "v", "<"]):
        y, x = self.robot
        match direction:
            case "^":
                path = [(ii, self.grid[ii][x]) for ii in range(y)]
                next_wall = max(ii for ii, c in path if c == "#")
                free = next(reversed([ii for ii, c in path if c == "."]), None)
                if free is not None and free > next_wall:
                    for ii in range(free, y):
                        self.grid[ii][x] = self.grid[ii + 1][x]
                    self.grid[y][x] = "."
                    self.robot = y - 1, x
            case ">":
                path = [
                    (ii, self.grid[y][ii]) for ii in range(x + 1, len(self.grid[0]))
                ]
                next_wall = min(ii for ii, c in path if c == "#")
                free = next((ii for ii, c in path if c == "."), None)
                if free is not None and free < next_wall:
                    self.grid[y][x + 1 : free + 1] = self.grid[y][x:free]
                    self.grid[y][x] = "."
                    self.robot = y, x + 1
            case "v":
                path = [(ii, self.grid[ii][x]) for ii in range(y + 1, len(self.grid))]
                next_wall = min(ii for ii, c in path if c == "#")
                free = next((ii for ii, c in path if c == "."), None)
                if free is not None and free < next_wall:
                    for ii in range(free, y, -1):
                        self.grid[ii][x] = self.grid[ii - 1][x]
                    self.grid[y][x] = "."
                    self.robot = y + 1, x
            case "<":
                path = [(ii, self.grid[y][ii]) for ii in range(x)]
                next_wall = max(ii for ii, c in path if c == "#")
                free = next(reversed([ii for ii, c in path if c == "."]), None)
                if free is not None and free > next_wall:
                    self.grid[y][free:x] = self.grid[y][free + 1 : x + 1]
                    self.grid[y][x] = "."
                    self.robot = y, x - 1

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

    @property
    def gps(self):
        boxes = [
            (ii, jj)
            for ii, row in enumerate(self.grid)
            for jj, c in enumerate(row)
            if c == "O"
        ]
        return sum(ii * 100 + jj for ii, jj in boxes)

    def __rich__(self):
        def render_pos(c: str):
            if c == "#":
                return f"[red]{c}[/]"
            elif c == "@":
                return f"[green]{c}[/]"
            return c

        s = "\n".join(map(lambda r: "".join(map(render_pos, r)), self.grid))
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
    movements = "".join(map(str.strip, movements.splitlines()))
    wh = Warehouse.from_str(warehouse)

    prog = Progress()
    t = prog.add_task("Progress", total=len(movements))
    lay = Layout()
    lay.split_column(Layout(Panel(prog), size=3), Layout(name="bort"))
    lay["bort"].split_row(
        Layout(wh, name="wh"),
        Layout(Panel(movements), name="mv"),
    )

    with Live(lay):
        for ii, d in enumerate(movements):
            wh.move_robot(d)  # pyright: ignore[reportArgumentType]
            lay["wh"].update(wh)
            s = "".join(
                f"[red]{m}[/]" if jj == ii else m for jj, m in enumerate(movements)
            )
            lay["mv"].update(Panel(s))
            prog.advance(t)
            time.sleep(0.002)
    return wh.gps


def part2(test: bool = False):
    return part1(test, part2=True)
