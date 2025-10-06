# Main program to drive SlothPU16

import argparse
import pathlib

from typing import List

import bitarray

import constants
import utils


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


if __name__ == "__main__":
    main()
