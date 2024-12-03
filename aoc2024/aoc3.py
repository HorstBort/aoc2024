import re
from aoc2024.get_input import get_input

test_input = """
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
""".strip()

test_input_2 = """
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
""".strip()


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(3)

    pairs = parse_mul_groups(input)

    return sum(a * b for a, b in pairs)


def parse_mul_groups(input: str):
    mul_groups: list[tuple[str]] = re.findall("mul\\((\\d{1,3}),(\\d{1,3})\\)", input)
    pairs = [map(int, pair) for pair in mul_groups]
    return pairs


def part2(test: bool = False):
    if test:
        input = test_input_2
    else:
        input = get_input(3)

    input = "".join(input.splitlines())
    re_to_cut = re.compile("don\\'t\\(\\).*?do\\(\\)")

    to_cut = list(re_to_cut.finditer(input))
    to_keep = [(0, to_cut[0].span()[0])]
    to_keep.extend([(m1.span()[1], m2.span()[0]) for m1, m2 in zip(to_cut, to_cut[1:])])
    to_keep.append((to_cut[-1].span()[1], len(input)))
    to_parse = "".join(input[a:b] for a, b in to_keep)
    pairs = parse_mul_groups(to_parse)

    return sum(a * b for a, b in pairs)
