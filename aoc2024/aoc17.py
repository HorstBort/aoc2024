from pathlib import Path
import time
from typing import final

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


DAY = int(Path(__file__).stem[3:])

Point = tuple[int, int]


@final
class Computer:
    ptr: int = 0

    def __init__(self, reg_A: int, reg_B: int, reg_C: int) -> None:
        self._registers = {"A": reg_A, "B": reg_B, "C": reg_C}
        self._output: list[int] = []
        self._program = []
        self._cycle = 0
        self._debug: tuple[str, int] = ("", 0)

    def run_program(self, program: str):
        self._cycle = 0
        bla = list(map(int, program.strip().split(",")))
        ops, values = bla[::2], bla[1::2]
        self._program = list(zip(ops, values))
        while self.ptr < len(bla) - 1:
            op = bla[self.ptr]
            v = bla[self.ptr + 1]
            self.instructions[op](self, v)
            time.sleep(0.1)
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
        panel_outout = Panel(f"Cycle: {self._cycle}\nOutput: {output}", title="Output")
        panel_debug = Panel(f"op: {self._debug[0]}\nv: {self._debug[1]}", title="Debug")

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
            return value
        else:
            raise ValueError("Corrupt address")

    def adv(self, value: int):
        value = self._combo(value)
        self._debug = "adv", value
        self._registers["A"] = self._registers["A"] // 2**value
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
        self._registers["C"] = self._registers["B"] ^ self._registers["C"]
        self.ptr += 2

    def out(self, value: int):
        value = self._combo(value)
        self._debug = "out", value
        self._output.append(value % 8)
        self.ptr += 2

    def bdv(self, value: int):
        self._debug = "bdv", value
        self._registers["B"] = self._registers["A"] // value**2
        self.ptr += 2

    def cdv(self, value: int):
        self._debug = "cdv", value
        self._registers["C"] = self._registers["A"] // value**2
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


def part1(test: bool = False, part2: bool = False):
    if test:
        if not part2:
            input = test_input
        else:
            input = test_input
    else:
        input = get_input(DAY)

    registers, program = input.strip().split("\n\n")
    register_values = [int(line.split(":")[1]) for line in registers.splitlines()]
    program = program.split(":")[1]
    c = Computer(*register_values)
    with Live(c):
        c.run_program(program)
    return c.output


def part2(test: bool = False):
    return part1(test, part2=True)
