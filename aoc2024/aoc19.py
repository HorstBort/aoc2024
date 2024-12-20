from pathlib import Path

from rich import print


from aoc2024.get_input import get_input

test_input = """
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
"""


DAY = int(Path(__file__).stem[3:])


def part1(test: bool = False, as_part2: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    print(input)


def part2(test: bool = False):
    return part1(test, as_part2=True)
