import importlib
from types import ModuleType


days = range(1, 26)

mods: list[ModuleType] = []
for ii in days:
    try:
        m = importlib.import_module(f"aoc2024.aoc{ii}")
    except ModuleNotFoundError:
        pass
    else:
        mods.append(m)


TEST_RESULTS = {
    1: (11, 31),
    2: (2, 4),
    3: (161, 48),
    4: (18, 9),
    5: (143, 123),
    6: (41, 6),
    7: (3749, 11387),
    8: (14, 9),
}


def test_days(subtests):
    for day, (res_1, res_2) in TEST_RESULTS.items():
        m = mods[day - 1]
        with subtests.test(day=day):
            assert m.part1(test=True) == res_1
        with subtests.test(day=day):
            assert m.part2(test=True) == res_2
