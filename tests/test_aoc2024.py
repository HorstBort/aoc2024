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
    9: (1928, 2858),
    10: (36, 81),
    11: (55312, None),
    12: (1930, None),
    13: (480, None),
    15: (10092, None),
    16: (7036, None),
    17: ("4,6,3,5,6,3,5,2,1,0", None),
    18: (22, (6, 1)),
    19: (6, None),
}


def test_days(subtests):
    for day, (res_1, res_2) in TEST_RESULTS.items():
        m = mods[day - 1]
        with subtests.test(day=day):
            assert m.part1(test=True) == res_1
        with subtests.test(day=day):
            assert m.part2(test=True) == res_2
