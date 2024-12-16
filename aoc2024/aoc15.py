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
    robot: Point
    walls: set[Point]
    boxes: set[Point]
    scale: int = 1
    shape: Point = (0, 0)

    def __post_init__(self):
        self.shape = (
            max(ii for ii, _ in self.walls | self.boxes) + 1,
            max(jj for _, jj in self.walls | self.boxes) + 1,
        )

    @classmethod
    def from_str(cls, s: str, scale: int = 1):
        grid = list(map(list, s.strip().splitlines()))
        robot = next(
            (ii, jj)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "@"
        )
        return Warehouse(
            robot,
            {
                (ii, jj)
                for ii, row in enumerate(grid)
                for jj, c in enumerate(row)
                if c == "#"
            },
            {
                (ii, jj)
                for ii, row in enumerate(grid)
                for jj, c in enumerate(row)
                if c == "O"
            },
            scale=scale,
        )

    def can_move_box(self, box: Point, d: Literal["^", ">", "v", "<"]) -> bool:
        if self.scale == 1:
            next_pos = self.next_pos(box, d)
            if next_pos in self.walls:
                return False
            elif next_pos in self.boxes:
                return self.can_move_box(next_pos, d)
            else:
                return True
        else:  # TODO: Part 2
            return True

    def move_box(self, box: Point, d: Literal["^", ">", "v", "<"]) -> bool:
        if self.scale == 1:
            next_pos = self.next_pos(box, d)
            if next_pos in self.walls:
                return False
            elif next_pos in self.boxes:
                bla = self.move_box(next_pos, d)
                if bla:
                    self.boxes.discard(box)
                    self.boxes.add(next_pos)
                return bla
            else:
                self.boxes.discard(box)
                self.boxes.add(next_pos)
                return True
        else:  # TODO: Part 2
            return True

    def next_pos(self, box: Point, d: Literal["^", ">", "v", "<"]):
        y, x = box
        match d:
            case "^":
                next_pos = (y - 1, x)
            case ">":
                next_pos = (y, x + 1)
            case "v":
                next_pos = (y + 1, x)
            case "<":
                next_pos = (y, x - 1)
        return next_pos

    def move_robot(self, d: Literal["^", ">", "v", "<"]):
        next_pos = self.next_pos(self.robot, d)
        if next_pos in self.walls:
            return
        elif next_pos in self.boxes:
            if self.move_box(next_pos, d):
                self.robot = next_pos
        else:
            self.robot = next_pos

    @property
    def gps(self):
        return sum(ii * 100 + jj for ii, jj in self.boxes)

    def __rich__(self):
        def render_pos(ii: int, jj: int):
            if (ii, jj) == self.robot:
                return "[green]@[/]"
            if self.scale == 1:
                if (ii, jj) in self.walls:
                    return "[red]#[/]"
                elif (ii, jj) in self.boxes:
                    return "[yellow]O[/]"
            elif self.scale == 2:
                if (ii, jj) in self.walls or (ii, jj + 1) in self.walls:
                    return "[red]#[/]"
                elif (ii, jj) in self.boxes:
                    return "[green][[/]"
                elif (ii, jj + 1) in self.boxes:
                    return "[green]][/]"
            return "."

        bort = [
            [render_pos(ii, jj) for jj in range(self.shape[1])]
            for ii in range(self.shape[0])
        ]
        s = "\n".join(map("".join, bort))
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
    wh = Warehouse.from_str(warehouse, scale=2 if part2 else 1)

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
            if test:
                time.sleep(0.01)
            else:
                time.sleep(0.001)
    return wh.gps


def part2(test: bool = False):
    return part1(test, part2=True)
