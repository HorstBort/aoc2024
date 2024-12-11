from functools import cache
from pathlib import Path
from rich import print


from aoc2024.get_input import get_input

test_input = """
125 17
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])


def part1(test: bool = False, blinks: int = 25):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    @cache
    def _blink(stone: int, blinks: int, depth: int = 0) -> int:
        if blinks == 0:
            return 1
        s = str(stone)
        if stone == 0:
            next = [1]
        elif len(s) % 2 == 0:
            next = [int(s[: len(s) // 2]), int(s[len(s) // 2 :])]
        else:
            next = [stone * 2024]
        return sum(_blink(n, blinks - 1, depth + 1) for n in next)

    stones = [v for v in map(int, input.split())]
    print(stones)
    s = 0
    for ii, stone in enumerate(stones):
        print(ii, stone)
        s += _blink(stone, blinks)

    return s


def part2(test: bool = False):
    if test:
        return
    else:
        return part1(test, 75)
