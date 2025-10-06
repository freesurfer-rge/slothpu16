N_BITS = 16
INSTR_BITS = 4
REG_BITS = 4

INSTRUCTIONS = {
    "add": 0,
    "sub": 1,
    "compare": 4,
    "nand": 5,
    "xor": 6,
    "barrel": 7,
    "loadb": 8,
    "loadw": 9,
    "storeb": 10,
    "storew": 11,
    "loadpc": 12,
    "branchzero": 13,
    "halt": 14,
    "set": 15,
}

INSTR_DECODE = [
    "add", "sub", "", "", "compare", "nand", "xor", "barrel", "loadb", "loadw", "storeb", "storew", "loadpc", "branchzero", "halt", "set"]
assert len(INSTR_DECODE)==2**INSTR_BITS
