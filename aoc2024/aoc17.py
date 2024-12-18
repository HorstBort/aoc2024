from pathlib import Path
from typing import final

import readchar

from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from aoc2024.get_input import get_input

test_input = """
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
"""

test_input_2 = """
Register A: 2024
Register B: 0
Register C: 0

Program: 0,3,5,4,3,0
"""


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@final
class Computer:
    ptr: int = 0

    def __init__(self) -> None:
        self._registers: dict[str, int] = {"A": 0, "B": 0, "C": 0}
        self._output: list[int] = []
        self._program = []
        self._cycle = 0
        self._debug: tuple[str, int] = ("", 0)

    def run_program(
        self,
        program: str,
        registers: dict[str, int],
        debug: bool = False,
        self_replicate: bool = False,
    ):
        self._registers = registers
        self._output = []
        self._cycle = 0
        self.ptr = 0
        bla = list(map(int, program.strip().split(",")))
        ops, values = bla[::2], bla[1::2]
        self._program = list(zip(ops, values))
        while self.ptr < len(bla) - 1 and (
            not self_replicate or self.output == program[: len(self.output)]
        ):
            op = bla[self.ptr]
            v = bla[self.ptr + 1]
            if debug:
                c = readchar.readkey()
                if c == "q":
                    raise Exception("Aborted")
            # else:
            #     time.sleep(0.001)
            self.instructions[op](self, v)
            self._cycle += 1

    def __rich__(self):
        t = Table.grid()
        table_register = Table("Name", "Value")
        for k, v in self._registers.items():
            table_register.add_row(k, str(v))
        table_program = Table("Pointer", "OPCODE", "OPERAND")
        for ii, (code, op) in enumerate(self._program):
            table_program.add_row(">" if ii * 2 == self.ptr else "", str(code), str(op))

        output = ",".join(map(str, self._output))
        panel_outout = Panel(f"{output}", title="Output")
        panel_debug = Panel(
            f"cycle: {self._cycle}\nop: {self._debug[0]}\nv: {self._debug[1]}",
            title="Debug",
        )

        t.add_row(
            Panel(table_register, title="Registers"),
            Panel(table_program, title="Program"),
            panel_debug,
            panel_outout,
        )
        return t

    def _combo(self, value: int):
        if 0 <= value < 4:
            return value
        elif value == 4:
            return self._registers["A"]
        elif value == 5:
            return self._registers["B"]
        elif value == 6:
            return self._registers["C"]
        elif value == 7:
            raise ValueError("Reserved")
        else:
            raise ValueError("Corrupt address")

    def adv(self, value: int):
        value = self._combo(value)
        self._debug = "adv", value
        self._registers["A"] = self._registers["A"] >> value
        self.ptr += 2

    def bxl(self, value: int):
        self._debug = "bxl", value
        self._registers["B"] = self._registers["B"] ^ value
        self.ptr += 2

    def bst(self, value: int):
        value = self._combo(value)
        self._debug = "bst", value
        self._registers["B"] = value % 8
        self.ptr += 2

    def jnz(self, value: int):
        self._debug = "jnz", value
        if self._registers["A"] == 0:
            self.ptr += 2
        else:
            self.ptr = value

    def bxc(self, value: int):
        self._debug = "bxc", value
        self._registers["B"] = self._registers["B"] ^ self._registers["C"]
        self.ptr += 2

    def out(self, value: int):
        value = self._combo(value)
        self._debug = "out", value
        self._output.append(value % 8)
        self.ptr += 2

    def bdv(self, value: int):
        value = self._combo(value)
        self._debug = "bdv", value
        self._registers["B"] = self._registers["A"] >> value
        self.ptr += 2

    def cdv(self, value: int):
        value = self._combo(value)
        self._debug = "cdv", value
        self._registers["C"] = self._registers["A"] >> value
        self.ptr += 2

    @property
    def output(self):
        return ",".join(map(str, self._output))

    instructions = {
        0: adv,
        1: bxl,
        2: bst,
        3: jnz,
        4: bxc,
        5: out,
        6: bdv,
        7: cdv,
    }


def part1(test: bool = False):
    if test:
        input = test_input
    else:
        input = get_input(DAY)

    registers, program = input.strip().split("\n\n")
    register_values = [int(line.split(":")[1]) for line in registers.splitlines()]
    program = program.split(":")[1]
    c = Computer()
    with Live(c):
        c.run_program(program, dict(zip(["A", "B", "C"], register_values)), debug=True)
    return c.output


def part2(test: bool = False):
    if test:
        input = test_input_2
    else:
        input = get_input(DAY)

    _, program = input.strip().split("\n\n")
    program = program.split(":")[1].strip()

    def bort(a: int):
        b = a % 8
        b = b ^ 1
        c = a >> b
        b = b ^ c
        a = a >> 3
        b = b ^ 6
        out = b % 8

        return a, out

    target = list(map(int, program.split(",")))

    bla: list[list[int]] = []
    for ii, t in enumerate(reversed(target)):
        poss: list[int] = [0] if not bla else bla[ii - 1]
        ranges = [(8 * p, 8 * (p + 1)) for p in poss]
        bla.append(
            [
                jj
                for r1, r2 in ranges
                for jj in range(r1, r2)
                if bort(jj)[1] == t and (not poss or bort(jj)[0] in poss)
            ]
        )

    print(target)
    return min(bla[-1])
