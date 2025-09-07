import bitarray.util

from constants import N_BITS, INSTR_BITS, REG_BITS, INSTRUCTIONS


def get_instruction(opcode: str, r_A: int, r_B: int, r_C: int) -> bitarray.bitarray:
    instr_bus = bitarray.util.zeros(N_BITS, endian="little")

    # Opcode is first four bits
    instr_bus[0:3] = bitarray.util.int2ba(
        INSTRUCTIONS[opcode], endian="little", length=INSTR_BITS
    )

    # r_A set by next four bits
    instr_bus[4:7] = bitarray.util.int2ba(r_A, endian="little", length=REG_BITS)

    # And then r_B
    instr_bus[8:11] = bitarray.util.int2ba(r_B, endian="little", length=REG_BITS)

    # r_C set by the final bits of the instruction
    instr_bus[12:15] = bitarray.util.int2ba(r_C, endian="little", length=REG_BITS)

    return instr_bus
