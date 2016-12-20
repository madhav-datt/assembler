import re
import itertools

# Regular expressions built using RegExr
NAME_NO_SPACE = "(?P<name>[a-zA-Z]+)"
NAME = NAME_NO_SPACE + "\s+"
LABEL = "(?P<label>[a-zA-Z_][_0-9a-zA-Z]+)\s*"
IMM = "(?P<imm>-?[0-9][x0-9A-Fa-f]*)\s*"
FIRST = "(?P<first>\$[0-9a-zA-Z]+)\s*"
SECOND = "(?P<second>\$[0-9a-zA-Z]+)\s*"
THIRD = "(?P<third>\$[0-9a-zA-Z]+)\s*"
COMMA = "\s*,\s*"

# Ignore commented lines and inline comments
EOL = "\s*(#.*)?$"
LINE_BEGIN = r"(?i)^[^#]*?"

# Compiled regular expression groups for assembly parsing
instruction_types = [
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + SECOND + COMMA + THIRD + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + SECOND + COMMA + LABEL + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + SECOND + COMMA + IMM + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + IMM + "\(\s*" + SECOND + "\s*\)\s*" + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + LABEL + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + COMMA + IMM + EOL),
    re.compile(LINE_BEGIN + NAME + FIRST + EOL),
    re.compile(LINE_BEGIN + NAME + LABEL + EOL),
    re.compile(LINE_BEGIN + NAME_NO_SPACE + EOL)
]

# Supported R-type instructions
r_type = {
    "add": (0x0, 0b100000, ["rd", "rs", "rt"]),
    "and": (0x0, 0b100100, ["rd", "rs", "rt"]),
    "jr": (0x0, 0b001000, ["rs"]),
    "nor": (0x0, 0b100111, ["rd", "rs", "rt"]),
    "or": (0x0, 0b100101, ["rd", "rs", "rt"]),
    "sll": (0x0, 0b000000, ["rd", "rt"]),
    "slt": (0x0, 0b101010, ["rd", "rs", "rt"]),
    "sra": (0x0, 0b000011, ["rd", "rt"]),
    "srl": (0x0, 0b000010, ["rd", "rt"]),
    "sub": (0x0, 0b100010, ["rd", "rs", "rt"]),
    "xor": (0x0, 0b100110, ["rd", "rs", "rt"])
}

# Supported I-type instructions
i_type = {
    "addi": (0b001000, ["rt", "rs"]),
    "andi": (0b001100, ["rt", "rs"]),
    "beq": (0b000100, ["rs", "rt"]),
    "bne": (0b000101, ["rs", "rt"]),
    "ori": (0b001101, ["rt", "rs"]),
    "sb": (0b101000, ["rt", "rs"]),
    "slti": (0b001010, ["rt", "rs"]),
    "sw": (0b101011, ["rt", "rs"]),
    "xori": (0b001110, ["rt", "rs"]),
    "lw": (0b100011, ["rt", "rs"])
}

# Supported J-type instructions
j_type = {
    "j": (0b000010, []),
    "jal": (0b000011, [])
}


class Register(object):
    """
    Class associated with registers
    """

    # Register and register aliases list
    names = [
        ["$0", "$zero", "$r0"],
        ["$1", "$at", "$r1"],
        ["$2", "$v0", "$r2"],
        ["$3", "$v1", "$r3"],
        ["$4", "$a0", "$r4"],
        ["$5", "$a1", "$r5"],
        ["$6", "$a2", "$r6"],
        ["$7", "$a3", "$r7"],
        ["$8", "$t0", "$r8"],
        ["$9", "$t1", "$r9"],
        ["$10", "$t2", "$r10"],
        ["$11", "$t3", "$r11"],
        ["$12", "$t4", "$r12"],
        ["$13", "$t5", "$r13"],
        ["$14", "$t6", "$r14"],
        ["$15", "$t7", "$r15"],
        ["$16", "$s0", "$r16"],
        ["$17", "$s1", "$r17"],
        ["$18", "$s2", "$r18"],
        ["$19", "$s3", "$r19"],
        ["$20", "$s4", "$r20"],
        ["$21", "$s5", "$r21"],
        ["$22", "$s6", "$r22"],
        ["$23", "$s7", "$r23"],
        ["$24", "$t8", "$r24"],
        ["$25", "$t9", "$r25"],
        ["$26", "$k0", "$r26"],
        ["$27", "$k1", "$r27"],
        ["$28", "$gp", "$r28"],
        ["$29", "$sp", "$r29"],
        ["$30", "$fp", "$r30"],
        ["$31", "$ra", "$r31"]
    ]

    def __init__(self, name):
        for i, n in enumerate(self.names):
            if name.lower() in n:
                self.id = i

    def binary(self):
        return self.id


class UnusedRegister(object):
    """
    Class associated with unused registers
    """
    def __init__(self):
        pass

    @staticmethod
    def binary():
        return 0


class Instruction(object):
    """
    Instructions class for R, I, J types
    """
    def __init__(self, program, position, name=None,
                 first=None, second=None, third=None,
                 imm=None, label=None):

        name = name.lower()
        # Check if provided instruction is a valid opcode
        if name not in r_type.keys() + i_type.keys() + j_type.keys():
            raise Exception("'%s' is not a valid opcode" % (name.lower()))

        self.program = program
        self.position = position
        self.name = name

        self.rs = UnusedRegister()
        self.rt = UnusedRegister()
        self.rd = UnusedRegister()

        # Verify that the right registers are present
        registers = (r_type[name][-1] if name in r_type else
                     i_type[name][-1] if name in i_type else
                     j_type[name][-1])
        rlist = [x for x in [first, second, third] if x is not None]

        for pos, reg in zip(registers, rlist):
            if pos == "rs":
                self.rs = Register(reg)
            elif pos == "rd":
                self.rd = Register(reg)
            elif pos == "rt":
                self.rt = Register(reg)

        if isinstance(imm, int):
            self.imm = imm
        else:
            self.imm = eval(imm) if imm is not None else 0
        self.label = label

    @staticmethod
    def parseline(program, position, line):
        global instruction_types
        for t in instruction_types:
            m = t.match(line)
            if m is not None:
                g = m.groupdict()

                if 'name' in g and g['name'].lower() == 'nop':
                    return PseudoInstruction(program, position, **m.groupdict())

                return Instruction(program=program, position=position, **g)

    def to_binary(self):
        # Handle R types
        if self.name in r_type.keys():
            b = 0
            b |= (self.rs.binary() << 21)  # rs
            b |= (self.rt.binary() << 16)  # rt
            b |= (self.rd.binary() << 11)  # rd

            b |= (self.imm << 6)
            b |= (r_type[self.name][1] << 0)  # function
            return b

        # Handle I types
        if self.name in i_type.keys():
            b = i_type[self.name][0] << 26
            b |= (self.rs.binary() << 21)  # rs
            b |= (self.rt.binary() << 16)  # rt

            # Extremely hacky branch check
            if self.label is not None:
                if "b" == self.name[0]:
                    z = self.program.label(self.label) - self.position - 1
                else:
                    z = self.program.label(self.label)
                b |= (z & 0xFFFF)  # label
            else:
                if "b" == self.name[0]:
                    b |= (self.imm >> 2 & 0xFFFF)  # imm
                else:
                    b |= (self.imm & 0xFFFF)  # imm

            return b

        # Handle J types
        if self.name in j_type.keys():
            b = (j_type[self.name][0]) << 26
            b |= (self.program.label(self.label) + (self.program.text_base >> 2))  # label
            return b

    # Size of instruction
    @staticmethod
    def size():
        return 1

    def bytes(self):
        b = self.to_binary()

        byte = [b >> 24,
                b >> 16 & 0xFF,
                b >> 8 & 0xFF,
                b & 0xFF]

        # Handle J type label issue
        if self.name in j_type.keys():
            byte = [b >> 24,
                    (b >> 16) + 16 & 0xFF,
                    b >> 8 & 0xFF,
                    b & 0xFF]

        return byte


class PseudoInstruction(object):
    """
    Instructions class for Pseudo Instruction nop
    """
    def __init__(self, program, position, name):
        self.name = name.lower()
        self.program = program
        self.position = position
        self.instructions = []

        if self.name == "nop":
            self.instructions.append(Instruction(self.program, position, "sll", "$0", "$0", "0x0"))

    def bytes(self):
        return list(itertools.chain(*[x.bytes() for x in self.instructions]))

    def size(self):
        return sum([x.size() for x in self.instructions])
