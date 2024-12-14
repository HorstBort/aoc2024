from dataclasses import dataclass
from pathlib import Path
import re
import time

from rich import print

from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

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

test_input_2 = """
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


def part1(test: bool = False, part2: bool = False):
    if test:
        input = test_input
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

        return Panel("\n".join(lines))

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
        with Live(lay):
            for _ in range(100):
                lay.update(print_grid(robots))
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
                time.sleep(1)
        res = None

    return res


def part2(test: bool = False):
    return part1(test, part2=True)
