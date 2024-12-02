from aoc2024.get_input import get_input

test_input = """
3   4
4   3
2   5
1   3
3   9
3   3
""".strip()


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(1)

    lines_int = [tuple(map(int, line.split())) for line in input.splitlines()]

    list_1 = [line[0] for line in lines_int]
    list_2 = [line[1] for line in lines_int]

    zipped = zip(sorted(list_1), sorted(list_2))
    res = sum(abs(l1 - l2) for l1, l2 in zipped)
    return res


def part2(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(1)

    lines_int = [tuple(map(int, line.split())) for line in input.splitlines()]

    list_1 = [line[0] for line in lines_int]
    list_2 = [line[1] for line in lines_int]

    res = sum(list_2.count(l1) * l1 for l1 in list_1)
    return res
