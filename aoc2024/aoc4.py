from collections.abc import Sequence
import re
from typing import Literal, TypeVar

from rich import print
from aoc2024.get_input import get_input

test_input = """
....XXMAS.
.SAMXMS...
...S..A...
..A.A.MS.X
XMASAMX.MM
X.....XA.A
S.S.S.S.SS
.A.A.A.A.A
..M.M.M.MM
.X.X.XMASX
""".strip()

test_input_2 = """
.M.S......
..A..MSMS.
.M.S.MAA..
..A.ASMSM.
.M.S.M....
..........
S.S.S.S.S.
.A.A.A.A..
M.M.M.M.M.
..........
""".strip()


T = TypeVar("T")


def transpose_array(arr: Sequence[Sequence[T]]):
    n_rows, n_cols = len(arr), len(arr[0])
    return [[arr[jj][ii] for jj in range(n_rows)] for ii in range(n_cols)]


def transpose_bort(array: Sequence[str]):
    return ["".join(r) for r in transpose_array(array)]


def match_array(arr: list[str]):
    phrase = "XMAS"
    matches_f = [[m.span() for m in re.finditer(phrase, r)] for r in arr]
    return matches_f


def print_matches(
    arr: list[str],
    mirror: bool = False,
    transpose: bool = False,
    shift: Literal["n", "r", "l"] = "n",
):
    arr_orig = arr[:]
    # print(arr)
    if shift == "l":
        arr = [
            ("." * (len(arr) - ii - 1) + row + "." * ii) for ii, row in enumerate(arr)
        ]
    elif shift == "r":
        arr = [
            ("." * ii + row + "." * (len(arr_orig) - ii - 1))
            for ii, row in enumerate(arr)
        ]
    # print(arr)
    if transpose:
        arr = transpose_bort(arr)
    # print(arr)
    if mirror:
        arr = [s[::-1] for s in arr]
    # print(arr)
    indices = match_array(arr)
    # print(indices)
    mark_indices = [{ii for x1, x2 in ids for ii in range(x1, x2)} for ids in indices]
    to_mark = [
        [ii in mi for ii in range(len(row))] for row, mi in zip(arr, mark_indices)
    ]

    # print(to_mark)
    if mirror:
        to_mark = [r[::-1] for r in to_mark]
    if transpose:
        to_mark = transpose_array(to_mark)
    # print(to_mark)
    if shift == "l":
        to_mark = [
            row[len(arr_orig) - 1 - ii : len(row) - ii]
            for ii, row in enumerate(to_mark)
        ]
    elif shift == "r":
        to_mark = [row[ii : len(arr_orig) + ii] for ii, row in enumerate(to_mark)]
    # print(to_mark)
    print_marked(arr_orig, to_mark)
    return sum(len(ii) for ii in indices), to_mark


def print_marked(arr: list[str], to_mark: list[list[bool]]):
    for row, tm in zip(arr, to_mark):
        chars = [f"[red]{c}[/red]" if mark else c for c, mark in zip(row, tm)]
        print("".join(chars))


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(4)

    rows = input.splitlines()
    print((len(rows), len(rows[0])))

    res_tot = 0
    to_mark = [[False] * len(row) for row in rows]
    print("\nForwards:\n")

    res, tm = print_matches(rows)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nBackwards:\n")
    res, tm = print_matches(rows, mirror=True)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nDown:\n")
    res, tm = print_matches(rows, transpose=True)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nUp:\n")
    res, tm = print_matches(rows, mirror=True, transpose=True)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nDiag TL-BR:\n")
    res, tm = print_matches(rows, shift="l", transpose=True, mirror=False)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nDiag TR-BL:\n")
    res, tm = print_matches(rows, shift="r", transpose=True, mirror=False)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nDiag BL-TR:\n")
    res, tm = print_matches(rows, shift="r", transpose=True, mirror=True)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nDiag BR-TL:\n")
    res, tm = print_matches(rows, shift="l", transpose=True, mirror=True)
    to_mark = [[a or b for a, b in zip(row1, row2)] for row1, row2 in zip(to_mark, tm)]
    res_tot += res

    print("\nTotal:\n")
    print_marked(rows, to_mark)

    return res_tot


def part2(test: bool = False):
    if test:
        input = test_input_2
    else:
        input = get_input(4)

    rows = input.splitlines()
    lr = len(rows[0])

    def test_A(row: int, col: int):
        return (
            0 < row < len(rows) - 1
            and 0 < col < lr - 1
            and (
                (
                    rows[row - 1][col - 1] == "M"
                    and rows[row - 1][col + 1] == "M"
                    and rows[row + 1][col + 1] == "S"
                    and rows[row + 1][col - 1] == "S"
                )
                or (
                    rows[row - 1][col - 1] == "S"
                    and rows[row - 1][col + 1] == "M"
                    and rows[row + 1][col + 1] == "M"
                    and rows[row + 1][col - 1] == "S"
                )
                or (
                    rows[row - 1][col - 1] == "S"
                    and rows[row - 1][col + 1] == "S"
                    and rows[row + 1][col + 1] == "M"
                    and rows[row + 1][col - 1] == "M"
                )
                or (
                    rows[row - 1][col - 1] == "M"
                    and rows[row - 1][col + 1] == "S"
                    and rows[row + 1][col + 1] == "S"
                    and rows[row + 1][col - 1] == "M"
                )
            )
        )

    centers = (
        (ii, m.start()) for ii, r in enumerate(rows) for m in re.finditer("A", r)
    )

    match = {(row, col) for row, col in centers if test_A(row, col)}

    inc = [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)]
    mark = [
        (row + inc_row, col + inc_col) for row, col in match for inc_row, inc_col in inc
    ]

    if test:
        out: list[str] = []
        for ii, row in enumerate(rows):
            chars = [
                f"[red]{c}[/red]" if (ii, jj) in mark else c for jj, c in enumerate(row)
            ]
            out.append("".join(chars))

        print("\n".join(out))

    # print(centers)
    # print(match)

    return len(match)
