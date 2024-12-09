from itertools import zip_longest
from pathlib import Path

from aoc2024.get_input import get_input

test_input = """
2333133121414131402
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])


def part1(test: bool = False, part2: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    as_int = list(map(int, input.strip()))

    files = as_int[::2]
    free = as_int[1::2]

    fragmented: list[int | None] = []
    for ii, (file, free) in enumerate(zip_longest(files, free, fillvalue=0)):
        fragmented.extend([ii] * file + [None] * free)

    print("".join(str(ii) if ii is not None else "." for ii in fragmented))

    last_file = next(
        ii for ii, v in reversed(list(enumerate(fragmented))) if v is not None
    )
    first_free = next(ii for ii, v in enumerate(fragmented) if v is None)
    print(last_file, first_free)
    while first_free < last_file:
        fragmented[first_free] = fragmented[last_file]
        fragmented[last_file] = None
        if test:
            print("".join(str(ii) if ii is not None else "." for ii in fragmented))
        else:
            print(first_free, last_file)
        last_file = next(
            ii for ii, v in reversed(list(enumerate(fragmented))) if v is not None
        )
        first_free = next(ii for ii, v in enumerate(fragmented) if v is None)

    checksum = sum(ii * v for ii, v in enumerate(fragmented) if v is not None)

    return checksum


def part2(test: bool = False):
    return part1(test, True)
