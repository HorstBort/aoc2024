from functools import cmp_to_key
from rich import print
from aoc2024.get_input import get_input

test_input = """
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
""".strip()

test_input_2 = """
""".strip()


def print_prefixed(s: str, pref: str = "    "):
    print(f"{pref}{s}")


def format_update_list(update: list[int]):
    return ", ".join(map(str, update))


def part1(test: bool = False, run_as_part_2: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(5)

    rules, updates = map(str.strip, input.split("\n\n"))

    rules = [tuple(map(int, pair.split("|"))) for pair in rules.splitlines()]
    updates = [list(map(int, line.split(","))) for line in updates.splitlines()]

    orders = {p: {p2 for p1, p2 in rules if p1 == p} for p, _ in rules}
    orders_reversed = {p: {p1 for p1, p2 in rules if p2 == p} for _, p in rules}

    def _cmp(v1: int, v2: int):
        if v1 in orders and v2 in orders[v1]:
            return -1
        elif v1 in orders_reversed and v2 in orders_reversed[v1]:
            return 1
        else:
            return 0

    for v1, v2 in rules:
        assert _cmp(v1, v2) < 0

    pages_ordered = sorted(
        {p for p in list(orders.keys()) + list(orders_reversed.keys())},
        key=cmp_to_key(_cmp),
    )

    res = 0
    res_2 = 0

    def _format_update(u: int, u2: int):
        if u not in pages_ordered:
            return f"[yellow]{u2}[/]"
        elif u == u2:
            return f"[green]{u2}[/]"
        else:
            return f"[red]{u2}[/]"

    for update in updates:
        upd_ordered = sorted(update, key=cmp_to_key(_cmp))
        ordered = update == upd_ordered
        print_prefixed(format_update_list(update))
        print_prefixed(format_update_list(upd_ordered))
        s = format_update_list(update)
        if ordered:
            res += update[len(update) // 2]
            print_prefixed(s, "[green]OK[/]: ")
        else:
            res_2 += upd_ordered[len(upd_ordered) // 2]
            print_prefixed(s, "[red]!![/]: ")
            se = ", ".join(_format_update(u, u2) for u, u2 in zip(update, upd_ordered))
            print_prefixed(se)
        print()

    if run_as_part_2:
        return res_2
    return res


def part2(test: bool = False):
    return part1(test, run_as_part_2=True)
