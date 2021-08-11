"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from assembly_commands import arithmetic_commands

PUSH_TYPE = "C_PUSH"
POP_TYPE = "C_POP"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Opens the output file and gets ready to write into it

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.filename: str = ''
        self.output_stream = output_stream
        self.sp = 0
        self.segments_pointers = {'local': 1, 'argument': 2, 'this': 3, 'that': 4}
        self.lines_counter = 0

    def write_line(self, line):
        self.lines_counter += 1
        self.output_stream.write(f"{line}\n")

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        commands = arithmetic_commands[command]
        for line in commands:
            if '{}' in line:
                line = line.format(self.lines_counter + 2)  # +2 in order to skip one line
            self.write_line(line)

    def sp_plus_plus(self):
        self.write_line(f"@{self.sp}")
        self.write_line(f"M=M+1")

    def write_pop_push_normal_segment(self, command: str, segment: str, index: int) -> None:
        # push: addr = segment_pointer + index; *sp = *addr; sp++
        # pop: addr = segment_pointer + index; sp--; *addr = *sp

        # pseudo code: addr = segment_pointer + index
        segment_pointer = self.segments_pointers[segment]
        self.write_line(f"@{index}")
        self.write_line(f"D=A")
        self.write_line(f"@{segment_pointer}")
        self.write_line(f"D=M+D")
        self.write_line(f"@addr")
        self.write_line(f"M=D")

        if command == PUSH_TYPE:
            # pseudo code: *sp = *addr
            self.write_line(f"@addr")
            self.write_line("A=M")
            self.write_line("D=M")
            self.write_line(f"@{self.sp}")
            self.write_line("A=M")
            self.write_line("M=D")

            # pseudo code: sp++
            self.sp_plus_plus()

        elif command == POP_TYPE:
            # pseudo code: sp--
            self.write_line(f"@{self.sp}")
            self.write_line(f"M=M-1")

            # pseudo code: *addr = *sp
            self.write_line(f"@{self.sp}")
            self.write_line("A=M")
            self.write_line("D=M")

            self.write_line(f"@addr")
            self.write_line("A=M")
            self.write_line("M=D")

        else:
            raise Exception(f"only push and pop commands are supported for segment {segment}")

    def write_push_pop_constant(self, command: str, index: int) -> None:
        if command == PUSH_TYPE:
            # pseudo: *sp = i; sp++
            self.write_line(f"@{index}")
            self.write_line(f"D=A")
            self.write_line(f"@{self.sp}")
            self.write_line("A=M")
            self.write_line("M=D")

            self.sp_plus_plus()

    def write_pop_push_static(self, command, index):
        if command == POP_TYPE:
            # pseudo code: sp--
            self.write_line(f"@{self.sp}")
            self.write_line(f"M=M-1")

            # pseudo code: *addr = *sp
            self.write_line(f"@{self.sp}")
            self.write_line("A=M")
            self.write_line("D=M")

            self.write_line(f"{self.filename.index}")
            self.write_line("M=D")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """

        if segment in self.segments_pointers.keys():  # if this is a normal segment
            self.write_pop_push_normal_segment(command, segment, index)
        elif segment == "constant":
            self.write_push_pop_constant(command, index)
        elif segment == "static":
            self.write_push_pop_static(command, index)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()
