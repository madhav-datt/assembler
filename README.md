# assembler

[![Python27](https://img.shields.io/badge/python-2.7-blue.svg)](https://github.com/madhav-datt/assembler)

A small assembler for the MIPS Assembly Architecture. Takes MIPS assembly code and outputs raw machine code. It supports the following instructions, and pseudoinstructions like `nop`.

## Supported Instructions
```MIPS
add
and
jr
nor
or
sll
slt
sra
srl
sub
xor
addi
andi
beq
bne
ori
sb
slti
sw
xori
lw
j
jal
```

## Getting Started
To use the assembler on an `asm` file:

```Shell
$ python assembler.py [-h] [-o filename] filename
```
