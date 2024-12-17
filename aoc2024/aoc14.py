from dataclasses import dataclass
from pathlib import Path
import re
import time

from rich import print

from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from aoc2024.get_input import get_input

test_input = """
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
""".strip()


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@dataclass
class Robot:
    uid: int
    pos: Point
    vel: Point

    @classmethod
    def from_str(cls, ii: int, s: str):
        m = re.match("^p=(\\d+),(\\d+)\\s+v=(-?\\d+),(-?\\d+)$", s.strip())
        if m is None:
            raise ValueError(s)
        p1, p2, v1, v2 = map(int, m.groups())
        return Robot(ii, (p1, p2), (v1, v2))


test_input_2 = """
p=4,2 v=-0,-0
p=3,3 v=-0,-0
p=5,3 v=-0,0
p=2,4 v=0,-0
p=6,4 v=0,0
""".strip()

test_input_2 = test_input


def part1(test: bool = False, part2: bool = False):
    if test:
        if not part2:
            input = test_input
        else:
            input = test_input_2
    else:
        input = get_input(DAY)

    robots = [Robot.from_str(ii, s) for ii, s in enumerate(input.strip().splitlines())]

    if test:
        s_x = 11
        s_y = 7
    else:
        s_x = 101
        s_y = 103

    def print_grid(robots: list[Robot]):
        lines = [
            "".join(
                str(len([r for r in robots if r.pos == (jj, ii)]))
                if any(r.pos == (jj, ii) for r in robots)
                else "."
                for jj in range(s_x)
            )
            for ii in range(s_y)
        ]
        # left = [r for r in robots if r.pos[0] < split]
        # right = [r for r in robots if r.pos[0] > split]
        #
        # left_sym = {(split - r.pos[0], r.pos[1]) for r in left}
        # right_sym = {(r.pos[0] - split, r.pos[1]) for r in right}

        t = Table.grid()
        t.add_row(
            Panel("\n".join(lines)),
            # Panel(f"{left_sym}, {right_sym}"),
        )
        return t

    if not part2:
        secs = 100
        robots = [
            Robot(
                r.uid,
                (
                    (r.pos[0] + secs * r.vel[0]) % s_x,
                    (r.pos[1] + secs * r.vel[1]) % s_y,
                ),
                r.vel,
            )
            for r in robots
        ]

        quadrants = [
            (0, 0, s_x // 2, s_y // 2),
            (s_x // 2 + 1, 0, s_x, s_y // 2),
            (0, s_y // 2 + 1, s_x // 2, s_y),
            (s_x // 2 + 1, s_y // 2 + 1, s_x, s_y),
        ]

        res = 1
        for q1, q2, q3, q4 in quadrants:
            nr_r = len(
                [r for r in robots if q1 <= r.pos[0] < q3 and q2 <= r.pos[1] < q4]
            )
            res *= nr_r
    else:
        lay = Layout()
        prog = Progress()
        loop = next(
            ii
            for ii in range(1, 1000000000)
            if all(
                (
                    (r.pos[0] + ii * r.vel[0]) % s_x,
                    (r.pos[1] + ii * r.vel[1]) % s_y,
                )
                == (r.pos[0], r.pos[1])
                for r in robots
            )
        )
        t = prog.add_task("Total", total=loop + 1)
        lay.split_column(Layout(Panel(prog), size=3), Layout(name="bort"))
        with Live(lay):
            ttl = 5
            treetop = [
                {(ii, jj)}
                | {(ii + a * n, jj + n) for n in range(1, ttl) for a in [-1, 0, 1]}
                for ii in range(ttl, s_x - ttl + 1)
                for jj in range(0, s_y - ttl + 1)
            ]
            known_hashes: set[int] = set()
            res = None
            for ii in range(loop):
                h = hash(frozenset((r.uid, r.pos) for r in robots))
                if h in known_hashes:
                    raise Exception(robots, ii)
                known_hashes.add(h)
                prog.update(t, completed=ii)
                # min_x = min(r.pos[0] for r in robots)
                # max_x = max(r.pos[0] for r in robots)
                # split = min_x + (max_x - min_x) // 2
                #
                # left = [r for r in robots if r.pos[0] < split]
                # right = [r for r in robots if r.pos[0] > split]
                #
                # sym = {(split - r.pos[0], r.pos[1]) for r in left} == {
                #     (r.pos[0] - split, r.pos[1]) for r in right
                # }

                # top_found = False
                top_found = any(tt <= {r.pos for r in robots} for tt in treetop)

                # raise Exception(treetop)

                # if sym or top_found:
                if top_found:
                    lay["bort"].update(print_grid(robots))
                    time.sleep(2)
                    res = ii
                    break

                robots = [
                    Robot(
                        r.uid,
                        (
                            (r.pos[0] + r.vel[0]) % s_x,
                            (r.pos[1] + r.vel[1]) % s_y,
                        ),
                        r.vel,
                    )
                    for r in robots
                ]

    return res


def part2(test: bool = False):
    return part1(test, part2=True)
