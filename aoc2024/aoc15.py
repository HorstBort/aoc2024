from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import readchar

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

test_input_2 = """
#######
#...#.#
#.....#
#..OO@#
#..O..#
#.....#
#######

<vv<<^^<<^^
"""

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
            max(jj for _, jj in self.walls | self.boxes) + self.scale,
        )

    @classmethod
    def from_str(cls, s: str, scale: int = 1):
        grid = list(map(list, s.strip().splitlines()))
        robot = next(
            (ii, jj * scale)
            for ii, row in enumerate(grid)
            for jj, c in enumerate(row)
            if c == "@"
        )
        return Warehouse(
            robot,
            {
                (ii, jj * scale)
                for ii, row in enumerate(grid)
                for jj, c in enumerate(row)
                if c == "#"
            },
            {
                (ii, jj * scale)
                for ii, row in enumerate(grid)
                for jj, c in enumerate(row)
                if c == "O"
            },
            scale=scale,
        )

    def can_move_box(self, box: Point, d: Literal["^", ">", "v", "<"]) -> bool:
        y, x = box
        match d:
            case "^":
                neighbours = {
                    (y - 1, x),
                    (y - 1, x - 1),
                    (y - 1, x + 1),
                }
            case ">":
                neighbours = {(y, x + 2)}
            case "v":
                neighbours = {
                    (y + 1, x),
                    (y + 1, x - 1),
                    (y + 1, x + 1),
                }
            case "<":
                neighbours = {(y, x - 2)}
        if neighbours & self.walls:
            return False
        if not neighbours & self.boxes:
            return True
        return all(self.can_move_box(n, d) for n in neighbours & self.boxes)

    def is_wall(self, pos: Point):
        return (self.scale == 1 and pos in self.walls) | (
            self.scale == 2
            and (pos in self.walls or (pos[0] - 1, pos[1]) in self.walls)
        )

    def is_box(self, pos: Point):
        return (self.scale == 1 and pos in self.boxes) | (
            self.scale == 2
            and (pos in self.boxes or (pos[0] - 1, pos[1]) in self.boxes)
        )

    def box_at(self, pos: Point):
        if pos in self.boxes:
            return pos
        elif self.scale == 2:
            bort = {pos, (pos[0], pos[1] - 1)} & self.boxes
            if bort:
                return bort.pop()

    def move_box(self, box: Point, d: Literal["^", ">", "v", "<"]) -> bool:
        next_pos = self.next_pos(box, d)
        if self.scale == 1:
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
        elif self.can_move_box(box, d):
            y, x = box
            match d:
                case "^":
                    neighbours = {
                        (y - 1, x),
                        (y - 1, x - 1),
                        (y - 1, x + 1),
                    } & self.boxes
                    for n in neighbours:
                        _ = self.move_box(n, d)
                case ">":
                    neighbours = {(y, x + 2)} & self.boxes
                    for n in neighbours:
                        _ = self.move_box(n, d)
                case "v":
                    neighbours = {
                        (y + 1, x),
                        (y + 1, x - 1),
                        (y + 1, x + 1),
                    } & self.boxes
                    for n in neighbours:
                        _ = self.move_box(n, d)
                case "<":
                    neighbours = {(y, x - 2)} & self.boxes
                    for n in neighbours:
                        _ = self.move_box(n, d)
            # if neighbours:
            #     raise Exception()
            self.boxes.discard(box)
            self.boxes.add(next_pos)
            return True
        else:
            return False

    def next_pos(self, box: Point, d: Literal["^", ">", "v", "<"], skip: bool = False):
        y, x = box
        match d:
            case "^":
                next_pos = (y - 1, x)
            case ">":
                next_pos = (y, x + (2 if skip else 1))
            case "v":
                next_pos = (y + 1, x)
            case "<":
                next_pos = (y, x - (2 if skip else 1))
        return next_pos

    def move_robot(self, d: Literal["^", ">", "v", "<"]):
        next_pos = self.next_pos(self.robot, d)
        if next_pos in self.walls or (
            self.scale == 2
            and (
                (d == "<" and self.next_pos(next_pos, d) in self.walls)
                or (d == "^" and self.next_pos(next_pos, "<") in self.walls)
                or (d == "v" and self.next_pos(next_pos, "<") in self.walls)
            )
        ):
            return
        elif self.scale == 1 and next_pos in self.boxes:
            if self.move_box(next_pos, d):
                self.robot = next_pos
        elif self.scale == 2:
            box = self.box_at(next_pos)
            if box is None:
                self.robot = next_pos
            else:
                can_move = self.can_move_box(box, d)
                if can_move:
                    _ = self.move_box(box, d)
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
                if (ii, jj) in self.walls or (ii, jj - 1) in self.walls:
                    return "[red]#[/]"
                elif (ii, jj) in self.boxes:
                    return "[green][[/]"
                elif (ii, jj - 1) in self.boxes:
                    return "[green]][/]"
            return "."

        bort = [
            [render_pos(ii, jj) for jj in range(self.shape[1])]
            for ii in range(self.shape[0])
        ]
        s = "\n".join(map("".join, bort))
        return Panel(s)

    def clone(self):
        return Warehouse(
            (self.robot[0], self.robot[1]),
            {w for w in self.walls},
            {b for b in self.boxes},
            self.scale,
            self.shape,
        )


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
    t_calc = prog.add_task("Calculating", total=len(movements))
    t_step = prog.add_task("Moving", total=len(movements))
    lay = Layout()
    lay.split_column(Layout(Panel(prog), size=4), Layout(name="bort"))
    lay["bort"].split_row(
        Layout(wh, name="wh"),
        Layout(Panel(movements), name="move"),
    )
    lay["move"].split_column(
        Layout(name="ii", size=3),
        Layout(name="mv"),
    )

    with Live(lay):
        cache: dict[int, Warehouse] = {0: wh.clone()}
        for ii, d in enumerate(movements):
            prog.advance(t_calc)
            wh.move_robot(d)  # pyright: ignore[reportArgumentType]
            cache[ii + 1] = wh.clone()

        ii = 0
        while test and ii in cache:
            lay["wh"].update(cache[ii])
            s = "".join(
                f"[red]{m}[/]" if jj == ii else m for jj, m in enumerate(movements)
            )
            lay["mv"].update(Panel(s))
            lay["ii"].update(Panel(str(ii)))
            prog.update(t_step, completed=ii)
            p = readchar.readkey()
            match p:
                case "n":
                    ii += 1
                case "p":
                    ii = max(ii - 1, 0)
    return wh.gps


def part2(test: bool = False):
    return part1(test, part2=True)
