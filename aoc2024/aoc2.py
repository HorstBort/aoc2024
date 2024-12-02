from collections.abc import Sequence
from aoc2024.get_input import get_input

test_input = """
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
""".strip()


def _test_line(line: Sequence[int]):
    is_sorted = list(line) == sorted(set(line)) or list(line) == sorted(
        set(line), reverse=True
    )
    diffs = [abs(a - b) for a, b in zip(line, line[1:])]
    return is_sorted and max(diffs) < 4


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(2)

    lines_int = [tuple(map(int, line.split())) for line in input.splitlines()]

    safe = [ll for ll in lines_int if _test_line(ll)]
    return len(safe)


def part2(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(2)

    lines_int = [list(map(int, line.split())) for line in input.splitlines()]

    def _line_options(line: list[int]):
        return [line[:ii] + line[ii + 1 :] for ii in range(len(line))]

    safe = [ll for ll in lines_int if any(_test_line(lo) for lo in _line_options(ll))]
    return len(safe)
