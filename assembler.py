#!/usr/bin/env python
#
# MIPS assembler
# CS141 Assignment 6
#
# Madhav Datt, Greg Yang
#

import argparse
import mips_prog

# Command line input argument parsing
parser = argparse.ArgumentParser(description="CS141 MIPS Assembler")
parser.add_argument('filename')
parser.add_argument('-o', '--output', default=argparse.SUPPRESS,
                    help="Output file path/name.machine", metavar="filename")
args = vars(parser.parse_args())

# Read input file
f = open(args['filename'])
lines = f.readlines()
new_lines = []
for line in lines:
    if ":" in list(line):
        a = line.split(":")
        a[0] += ":\n"
    else:
        a = [line]

    new_lines += a

lines = [x.replace("\n", "") for x in new_lines]
f.close()

mp = mips_prog.MIPSProg()
mp.add_lines(lines)

try:
    # Output file from user, optional argument
    output = open(args['output'], 'w')
except KeyError:
    # Default output file name
    # [input_file_name].machine
    output = open(args['filename'][:-4] + '.machine', 'w')

_bin = mp.bytes()
for j in range(len(_bin) / 4):
    output.write("%02x%02x%02x%02x\n" % tuple(_bin[j * 4:j * 4 + 4]))

output.close()
