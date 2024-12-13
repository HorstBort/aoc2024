from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import re

from rich import print

from aoc2024.get_input import get_input

test_input = """
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@dataclass
class Block:
    inc_a: Point
    inc_b: Point
    prize: Point

    @classmethod
    def from_string(cls, s: str, offset: int = 0):
        s_a, s_b, s_p = s.strip().splitlines()
        m_a = re.match("^Button\\ A:\\ X\\+(\\d+),\\ Y\\+(\\d+)$", s_a)
        m_b = re.match("^Button\\ B:\\ X\\+(\\d+),\\ Y\\+(\\d+)$", s_b)
        m_p = re.match("^Prize:\\ X=(\\d+),\\ Y=(\\d+)$", s_p)
        if m_a is None or m_b is None or m_p is None:
            raise ValueError(s)
        return Block(
            tuple(map(int, m_a.groups())),
            tuple(map(int, m_b.groups())),
            tuple([v + offset for v in tuple(map(int, m_p.groups()))]),
        )

    def play(self):
        # print(self, max_a, max_b)

        p_2 = self.prize[1]
        a_2 = self.inc_a[1]
        a_1 = self.inc_a[0]
        p_1 = self.prize[0]
        b_2 = self.inc_b[1]
        b_1 = self.inc_b[0]
        y = Fraction((p_2 - Fraction(a_2, a_1) * p_1), (b_2 - Fraction(a_2, a_1) * b_1))
        x = Fraction((p_1 - y * b_1), a_1)
        if x.is_integer() and y.is_integer():
            return 3 * x + y
        else:
            return 0


def part1(test: bool = False, offset: int = 0):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    blocks = list(map(lambda v: Block.from_string(v, offset), input.split("\n\n")))

    total = 0
    for block in blocks:
        c = block.play()
        print(block, c)
        total += c

    return total


def part2(test: bool = False):
    return part1(test, offset=10000000000000)
