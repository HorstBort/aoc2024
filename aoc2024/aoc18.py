from pathlib import Path

from rich import print


from aoc2024.get_input import get_input

test_input = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    print(input)


def part2(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    return part1(test)
