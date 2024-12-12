from pathlib import Path
from rich import print


from aoc2024.get_input import get_input

test_input = """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
""".strip()

test_input_2 = """
""".strip()

DAY = int(Path(__file__).stem[3:])


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    garden = input.splitlines()
    left = {(ii, jj) for ii, row in enumerate(garden) for jj, _ in enumerate(row)}

    s_ii, s_jj = len(garden), len(garden[0])

    areas: list[tuple[str, set[tuple[int, int]]]] = []

    def grab_area(
        marker: str,
        pos: tuple[int, int],
        bort: set[tuple[int, int]] | None = None,
    ) -> set[tuple[int, int]]:
        if bort is None:
            bort = {pos}
        ii, jj = pos
        neighbours = {
            (ii + bla, jj + blub)
            for bla, blub in [(-1, 0), (0, 1), (1, 0), (0, -1)]
            if 0 <= ii + bla < s_ii
            and 0 <= jj + blub < s_jj
            and garden[ii + bla][jj + blub] == marker
        }
        for n in neighbours - bort:
            bort.add(n)
            _ = grab_area(marker, n, bort)
        return bort

    while left:
        ii, jj = left.pop()
        m = garden[ii][jj]
        area = grab_area(m, (ii, jj))
        areas.append((m, area))
        left -= area

    # print(areas)

    cost: list[tuple[str, int, int]] = list()
    for m, area in areas:
        padded = [
            (ii + inc_ii, jj + inc_jj)
            for ii, jj in area
            for inc_ii, inc_jj in [(-1, 0), (0, 1), (1, 0), (0, -1)]
        ]
        fence = [p for p in padded if p not in area]

        def _render_pos(pos: tuple[int, int]):
            if pos in area:
                return m
            elif pos in fence:
                return "#"
            else:
                return "."

        if test:
            ii_min, ii_max = min(ii for ii, _ in padded), max(ii for ii, _ in padded)
            jj_min, jj_max = min(jj for _, jj in padded), max(jj for _, jj in padded)

            grid = [
                [_render_pos((ii, jj)) for jj in range(jj_min, jj_max + 1)]
                for ii in range(ii_min, ii_max + 1)
            ]
            print(f"\n{m}: area: {len(area)}, fence: {len(fence)}\n")
            print("\n".join("".join(row) for row in grid))
        cost.append((m, len(area), len(fence)))
    if test:
        print(cost)
    return sum(a * f for _, a, f in cost)


def part2(test: bool = False):
    if test:
        return
    else:
        return part1(test)
