#
# MIPS assembler
# CS141 Assignment 6
#
# Madhav Datt, Greg Yang
#

import itertools
import re
import sys
import traceback

from instruction import Instruction


class MIPSProg:
    def __init__(self, lines=None):
        self.text_base = 0
        self.data_base = 0x00400000
        self.instructions = []
        self.data = []
        self.labels = {}
        self.defines = {}

        if lines is not None:
            for line in lines:
                self.handle_line(line)

    def add_lines(self, lines):
        for line in lines:
            self.handle_line(line)

    def handle_line(self, line):
        loc = sum([x.size() for x in self.instructions])

        for replace, value in self.defines.iteritems():
            line = re.sub(replace, value, line)

        if re.match("^\s*$", line) is not None:
            return

        try:
            m = re.match(r'''^\s*\.DEFINE\s*(?P<label>[_a-zA-Z0-9]+)\s*(?P<value>.*)$''', line)
            if m is not None:
                self.defines[m.group('label')] = m.group('value')
                return

            m = re.match(r'''^\s*\.STRING\s*(?P<label>[_a-zA-Z0-9]+)\s*(?P<str>".*")''', line)
            if m is not None:
                self.reg_data_label(m.group('label'), eval(m.group('str')))
                return

            m = re.match("^\s*(?P<label>[_a-zA-Z0-9]+):\.*$", line)
            if m is not None:
                self.reg_label(m.group('label'), loc)
                return

            # Ignore remaining parts
            m = re.match("^\s*#.*$", line)
            if m is not None:
                return

            inst = Instruction.parseline(self, loc, line)
            self.instructions.append(inst)
        except Exception as e:
            print traceback.format_exc(e)
            sys.exit(1)

    def reg_label(self, label, address):
        self.labels[label] = address

    def reg_data_label(self, label, string):
        string += "\0"
        position = sum([len(x) for x in self.data])
        self.labels[label] = self.data_base + position
        self.data.append(string)

    def label(self, label):
        """
        Return label position
        """
        # Avoid function calling string objects
        if hasattr(label, '__call__'):
            value = label()
            return value

        return self.labels[label]

    def bytes(self):
        return list(itertools.chain(*[x.bytes() for x in self.instructions]))
