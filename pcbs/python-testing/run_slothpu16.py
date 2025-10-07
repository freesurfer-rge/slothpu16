# Main program to drive SlothPU16

import argparse
import pathlib
import time

from typing import List

import bitarray

import constants
import utils

from pi_backplane import _Input, _Output

STAGE_DELAY = 0.1
RESET_DELAY = 0.1


def parse_arguments():
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        "--input_file",
        type=pathlib.Path,
        required=True,
        help="Path to SlothPU assembler file",
    )

    args = parser.parse_args()

    return args


def get_register(reg_part: str) -> int:
    assert reg_part[0] == "R", f"Unrecognised register identifier: {reg_part}"

    reg = int(reg_part[1:])
    assert reg >= 0 and reg < 2 ** constants.REG_BITS, f"Bad register value: {reg_part}"
    return reg


def convert_machinecode(line: str) -> List[int]:
    parts = line.split()
    instr = parts[0]

    if instr == "set":
        assert len(parts) == 3, f"Bad instruction: {line}"
        value = int(parts[1])
        assert value >= 0 and value < 256, f"Bad set value: {value}"
        r_B, r_A = divmod(value, 2 ** constants.REG_BITS)
        r_C = get_register(parts[2])
    elif instr == "branchzero":
        assert len(parts) == 3, f"Bad instruction: {line}"
        r_A = get_register(parts[1])
        r_B = get_register(parts[2])
        r_C = 0
    elif instr == "halt":
        assert len(parts) == 1, f"Bad instruction: {line}"
        r_A = 0
        r_B = 0
        r_C = 0
    else:
        assert len(parts) == 4, f"Bad instruction: {line}"
        r_A = get_register(parts[1])
        r_B = get_register(parts[2])
        r_C = get_register(parts[3])

    instr_bits = utils.get_instruction(instr, r_A, r_B, r_C)
    print(f"instr={instr_bits}")
    assert len(instr_bits) == constants.N_BITS, f"{len(instr_bits)}"

    low_byte = bitarray.util.ba2int(instr_bits[0:8])
    assert low_byte < 256, "Sanity check"
    high_byte = bitarray.util.ba2int(instr_bits[8:16])
    assert high_byte < 256, "Sanity check"

    return [low_byte, high_byte]


def process_assembler(lines: List[str]) -> List[int]:
    COMMENT_CHAR = "#"

    result = []

    for l in lines:
        pruned_line = l.split(COMMENT_CHAR)[0].strip()
        if len(pruned_line) > 0:
            print(f"'{pruned_line}'")
            bytes = convert_machinecode(pruned_line)
            assert len(bytes) == 2
            result += bytes

    return result

def show_buses(input: _Input):
    time.sleep(0.01)
    input.recv()
    print(f"A={input.read_bus('A')}")
    print(f"B={input.read_bus('B')}")
    print(f"C={input.read_bus('C')}")
    instr = input.read_bus("Instruction")
    print(f"instr={instr}")
    instr_bits = bitarray.util.int2ba(instr, length=constants.N_BITS, endian="little")
    print(f"Instr= {instr_bits[0:4]} r_A={instr_bits[4:8]} r_B={instr_bits[8:12]} r_C={instr_bits[12:16]}")

def advance_stage():
    #_ = input()
    time.sleep(STAGE_DELAY)


def run_processor(memory: List[int]):
    output = _Output()
    input = _Input()

    output.set_oe("Instruction", True)
    output.set_oe("Cycle", False)
    output.set_oe("Reset", False)

    output.set_reset(True)
    output.send()
    time.sleep(RESET_DELAY)
    output.set_reset(False)
    output.send()
    time.sleep(RESET_DELAY)
    output.set_reset(True)
    output.send()
    time.sleep(RESET_DELAY)

    while True:
        # =====================
        # Instruction Fetch
        print("Instruction Fetch ========")
        output.set_cycle(0)
        output.send()

        input.recv()
        a_val = input.read_bus("A")
        assert a_val % 2 == 0, f"Instruction Fetch: {a_val}"
        print(f"Instr location: {a_val}")

        instruction = memory[a_val] + (256 * memory[a_val + 1])
        print(f"Instruction={instruction}")
        output.set_oe("B", False)
        output.set_bus("B", instruction)
        output.send()
        show_buses(input)
        advance_stage()

        # =====================
        # Instruction store
        print("Instruction store ========")
        output.set_cycle(1)
        output.send()
        show_buses(input)

        output.set_oe("B", True)
        advance_stage()

        # =====================
        # Decode/Execute
        print("Decode/Execute ========")
        output.set_cycle(2)
        output.send()

        input.recv()
        instr_val = input.read_bus("Instruction")
        instr = constants.INSTR_DECODE[instr_val % (2 ** constants.INSTR_BITS)]
        print(f"instr = {instr}")
        assert len(instr) > 0, f"Failed to decode {instr_val}"
        if instr in ["loadb", "loadw", "storeb", "storew"]:
            raise NotImplementedException(instr)
        show_buses(input)
        
        advance_stage()

        # ====================
        # Commit
        print("Commit =========")
        output.set_cycle(3)
        output.send()
        show_buses(input)

        # In case we wrote from memory....
        output.set_oe("C", True)
        advance_stage()

        # ====================
        # PC Update
        print("PC Update =======")
        output.set_cycle(4)
        output.send()
        show_buses(input)

        output.set_oe("A", True)
        output.set_oe("B", True)
        output.set_oe("C", True)
        advance_stage()


def main():
    args = parse_arguments()

    with open(args.input_file, "r") as af:
        assembler_lines = af.readlines()
    print(f"Read {len(assembler_lines)} lines")

    memory = process_assembler(assembler_lines)
    print("Assembly complete")

    # Zero initialise the remainder of the memory
    for _ in range(len(memory), 2 ** constants.N_BITS):
        memory.append(0)
    print(f"Mem Size: {len(memory)}")

    run_processor(memory)


if __name__ == "__main__":
    main()
