from pathlib import Path

from aoc2024.get_input import get_input

test_input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])


def part1(test: bool = False, part2: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    grid = [list(map(int, line)) for line in input.strip().splitlines()]

    shape = len(grid), len(grid[0])

    start_positions = [
        (ii, jj) for ii, row in enumerate(grid) for jj, v in enumerate(row) if v == 0
    ]
    BORT = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def _check_pos(ii: int, jj: int, heads: list[tuple[int, int]] | None = None):
        if heads is None:
            heads = list()
        h = grid[ii][jj]
        if h == 9:
            heads.append((ii, jj))
        elif h < 9:
            for inc_i, inc_j in BORT:
                next_ii = ii + inc_i
                next_jj = jj + inc_j
                if (
                    0 <= next_ii < shape[0]
                    and 0 <= next_jj < shape[1]
                    and grid[next_ii][next_jj] == h + 1
                ):
                    _ = _check_pos(next_ii, next_jj, heads)
        return heads

    heads_by_start: dict[tuple[int, int], list[tuple[int, int]]] = dict()
    for sp in start_positions:
        heads_by_start[sp] = _check_pos(sp[0], sp[1])

    for sp, heads in heads_by_start.items():
        print(sp, len(heads))
    if not part2:
        return sum(len(set(heads)) for heads in heads_by_start.values())
    else:
        return sum(len(heads) for heads in heads_by_start.values())


def part2(test: bool = False):
    return part1(test, True)
