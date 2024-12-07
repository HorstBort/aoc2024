import itertools

from rich import print

from aoc2024.get_input import get_input

test_input = """
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
""".strip()

test_input_2 = """
""".strip()


def add(a: int, b: int):
    return a + b


def mul(a: int, b: int):
    return a * b


def concat(a: int, b: int):
    return int(f"{a}{b}")


def _parse_line(line: str):
    res, operands = line.split(":")
    operands = list(map(int, operands.split()))
    return int(res), operands


def part1(test: bool = False, part2: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(7)

    all_ops = [add, mul]
    if part2:
        all_ops.append(concat)

    bort = list(map(_parse_line, input.splitlines()))
    valid: set[int] = set()
    for expected, inp in bort:
        op_combinations = list(itertools.product(*[all_ops] * (len(inp) - 1)))
        # print((expected, inp))
        for ops in op_combinations:
            res = inp[0]
            for op, v in zip(ops, inp[1:]):
                res = op(res, v)
            # print(ops, res)
            if res == expected:
                print(f"Wurst: {res}")
                valid.add(res)
                break

    return sum(valid)


def part2(test: bool = False):
    return part1(test, True)
