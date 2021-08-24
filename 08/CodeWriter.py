"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from arithmetic_commands import assembly_commands, BRANCH_SKIP, SUB_COMMAND

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
        self.segments_pointers = {'local': "LCL", 'argument': "ARG", 'this': "THIS", 'that': "THAT"}

        self.temp_addr = 5
        self.lines_counter = 0
        self.files_counter = 0
        self.calls_count = 0

    def write_line(self, line):
        self.lines_counter += 1
        self.output_stream.write(f"{line}\n")

    def write_comment_line(self, line):
        self.output_stream.write(f"{line}\n")

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename
        self.files_counter += 1

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        commands = assembly_commands[command]
        for line in commands:
            if '{}' in line:
                line = line.format(self.lines_counter + BRANCH_SKIP)  # +4 in order to skip some lines and create
                # branches
            self.write_line(line)

    def _sp_plus_plus(self):
        # sp++
        self.write_line("@SP")
        self.write_line(f"M=M+1")

    def _sp_minus_minus(self):
        # sp--
        self.write_line(f"@SP")
        self.write_line("M=M-1")

    def _d_eq_ast_address(self, address):
        # D = *address
        self.write_line(f"@{address}")
        self.write_line("A=M")
        self.write_line("D=M")

    def _ast_sp_eq_d(self):
        # *SP = D
        self.write_line(f"@SP")
        self.write_line("A=M")
        self.write_line("M=D")

    def _d_eq_ast_sp(self):
        # D = *SP
        self._d_eq_ast_address("SP")

    def _write_push_pop_given_addr(self, command, segment):
        # write push pop of value in address
        if command == PUSH_TYPE:
            # pseudo code: *sp = *addr
            self.write_line("@addr")
            self.write_line("A=M")
            self.write_line("D=M")
            self._ast_sp_eq_d()

            # pseudo code: sp++
            self._sp_plus_plus()

        elif command == POP_TYPE:
            # pseudo code: sp--
            self._sp_minus_minus()

            # pseudo code: *addr = *sp
            self._d_eq_ast_sp()

            self.write_line("@addr")
            self.write_line("A=M")
            self.write_line("M=D")

        else:
            raise Exception(f"only push and pop commands are supported for segment {segment}")

    def _write_push_pop_normal_segment(self, command: str, segment: str, index: int) -> None:
        # write push pop for standard memory segments

        # push: addr = segment_pointer + index; *sp = *addr; sp++
        # pop: addr = segment_pointer + index; sp--; *addr = *sp

        # pseudo code: addr = *segment_pointer + index
        segment_pointer = self.segments_pointers[segment]
        self.write_line(f"@{index}")
        self.write_line("D=A")
        self.write_line(f"@{segment_pointer}")
        self.write_line("D=M+D")
        self.write_line("@addr")
        self.write_line("M=D")

        self._write_push_pop_given_addr(command, segment)

    def _write_push_pop_constant(self, command: str, index: int) -> None:
        # write push pop for constant segment
        if command == PUSH_TYPE:
            # pseudo: *sp = i; sp++
            self.write_line(f"@{index}")
            self.write_line("D=A")
            self.write_line("@SP")
            self.write_line("A=M")
            self.write_line("M=D")

            self._sp_plus_plus()

    def _write_push_pop_static(self, command, index):
        # write push pop for static segment

        if command == PUSH_TYPE:
            # pseudo code: *sp = variable
            self.write_line(f"@{self.filename}.{index}")
            self.write_line("D=M")
            self._ast_sp_eq_d()

            # pseudo code: sp++
            self._sp_plus_plus()

        if command == POP_TYPE:
            # pseudo code: sp--
            self._sp_minus_minus()

            # pseudo code: variable = *sp
            self._d_eq_ast_sp()
            self.write_line(f"@{self.filename}.{index}")
            self.write_line("M=D")

    def _set_address(self, address):
        # make value in address equal D

        self.write_line(f"@{address}")
        self.write_line("D=A")
        self.write_line("@addr")
        self.write_line("M=D")

    def _write_push_pop_temp(self, command, index):
        # write push pop for temp segment

        # pseudo code: addr = temp_addr + index
        self._set_address(self.temp_addr + index)
        self._write_push_pop_given_addr(command, "temp")

    def _write_push_pop_pointer(self, command, index):
        # write push pop for pointer segment

        pseudo_segment_mapping = {0: "this", 1: "that"}
        try:
            pseudo_segment_pointer = pseudo_segment_mapping[index]
            pseudo_segment_symbol = self.segments_pointers[pseudo_segment_pointer]
        except KeyError:
            raise Exception("only indexes 0 and 1 are supported for segment pointer")

        if command == PUSH_TYPE:
            # self._d_eq_ast_address(pseudo_segment_pointer)
            self.write_line(f"@{pseudo_segment_symbol}")
            self.write_line(f"D=M")
            self._ast_sp_eq_d()
            self._sp_plus_plus()
        elif command == POP_TYPE:
            self._sp_minus_minus()
            self._d_eq_ast_sp()
            self.write_line(f"@{pseudo_segment_symbol}")
            # self.write_line("A=M")
            self.write_line("M=D")
        else:
            raise Exception(f"only push and pop commands are supported for segment pointer")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """

        if segment in self.segments_pointers.keys():  # if this is a normal segment
            self._write_push_pop_normal_segment(command, segment, index)
        elif segment == "constant":
            self._write_push_pop_constant(command, index)
        elif segment == "static":
            self._write_push_pop_static(command, index)
        elif segment == "temp":
            self._write_push_pop_temp(command, index)
        elif segment == "pointer":
            self._write_push_pop_pointer(command, index)
        else:
            raise Exception(f"segment {segment} not supported")

    def write_init(self):
        self.write_comment_line("// init")
        self.write_line("@256")
        self.write_line("D=A")
        self.write_line("@SP")
        self.write_line("M=D")
        self.write_call("Sys.init", "0")

    def write_label(self, label: str):
        self.write_line(f"({label})")

    def write_goto(self, label: str):
        self.write_line(f"@{label}")
        self.write_line("0;JMP")

    def write_if(self, label: str):
        self.write_line("@SP")
        self.write_line("A=M-1")
        self.write_line("D=M")
        self._sp_minus_minus()
        self.write_line(f"@{label}")
        self.write_line("D;JNE")

    def write_function(self, func_name: str, num_vars: str):
        self.write_line(f"({func_name})")
        for _ in range(int(num_vars)):
            self.write_push_pop(PUSH_TYPE, "constant", 0)

    def write_call(self, func_name: str, num_args: str):
        self.calls_count += 1
        self.write_line("@6666")
        self._push_label(f"return-{func_name}{self.calls_count}")  # push return-address
        self._push_var("LCL")  # push LCL
        self._push_var("ARG")  # push ARG
        self._push_var("THIS")  # push THIS
        self._push_var("THAT")  # push THAT

        # ARG = SP - num_args - 5
        self._sub_from_var("SP", int(num_args) + 5)
        self._pop_to_var("ARG")

        # LCL = SP
        self.write_line("@SP")
        self.write_line("D=M")
        self.write_line("@LCL")
        self.write_line("M=D")

        self.write_line(f"@{func_name}")  # go and execute func
        self.write_line("0;JMP")

        self.write_line(f"(return-{func_name}{self.calls_count})")

    def _push_var(self, pointer_name: str):
        self.write_line(f"@{pointer_name}")
        self.write_line("D=M")
        self.write_line("@SP")
        self.write_line("A=M")
        self.write_line("M=D")
        self._sp_plus_plus()

    def _push_label(self, var_name: str):
        self.write_line(f"@{var_name}")
        self.write_line("D=A")
        self.write_line("@SP")
        self.write_line("A=M")
        self.write_line("M=D")
        self._sp_plus_plus()

    def _pop_to_var(self, var_name: str):
        self.write_line("@SP")
        self.write_line("A=M-1")
        self.write_line("D=M")
        self.write_line(f"@{var_name}")
        self.write_line("M=D")
        self._sp_minus_minus()

    def _pop_pointer_to_var(self, var_name: str):
        self.write_line("@SP")
        self.write_line("A=M-1")
        self.write_line("A=M")
        self.write_line("D=M")
        self.write_line(f"@{var_name}")
        self.write_line("M=D")
        self._sp_minus_minus()

    def _sub_from_var(self, pointer_name: str, value: int):
        self._push_var(pointer_name)
        self.write_push_pop(PUSH_TYPE, "constant", value)
        self.write_arithmetic(SUB_COMMAND)

    def _ast_stack_top(self):
        self.write_line("@SP")
        self.write_line("A=M-1")
        self.write_line("A=M")
        self.write_line("D=M")
        self.write_line("@SP")
        self.write_line("A=M-1")
        self.write_line("M=D")

    def write_return(self):
        self.write_line("@1234")
        # FRAME=LCL
        self.write_line("@LCL")
        self.write_line("D=M")
        self.write_line("@FRAME")
        self.write_line("M=D")

        # RET = *(FRAME-5)
        self._sub_from_var("FRAME", 5)
        self._ast_stack_top()
        self._pop_to_var("RET")

        self.write_push_pop(POP_TYPE, "argument", 0)  # *ARG=return_value #TODO check!!!

        # future_SP=ARG+1
        self.write_line("@ARG")
        self.write_line("D=M+1")
        self.write_line("@future_SP")
        self.write_line("M=D")

        # THAT = *(FRAME-1)
        self._sub_from_var("FRAME", 1)
        self._ast_stack_top()
        self.write_push_pop(POP_TYPE, "pointer", 1)

        # THIS = *(FRAME-2)
        self._sub_from_var("FRAME", 2)
        self._ast_stack_top()
        self.write_push_pop(POP_TYPE, "pointer", 0)

        # ARG = *(FRAME-3)
        self._sub_from_var("FRAME", 3)
        self._pop_pointer_to_var("ARG")

        # LCL = *(FRAME-4)
        self._sub_from_var("FRAME", 4)
        self._pop_pointer_to_var("LCL")

        self.write_line("@future_SP")
        self.write_line("D=M")
        self.write_line("@SP")
        self.write_line("M=D")

        # goto RET
        self.write_line("@RET")
        self.write_line("A=M")
        self.write_line("0;JMP")

    def write_branching(self, command_type, *args):
        write_functions_dict = {"C_LABEL": self.write_label,
                                "C_GOTO": self.write_goto,
                                "C_IF": self.write_if,
                                "C_RETURN": self.write_return,
                                "C_CALL": self.write_call,
                                "C_FUNCTION": self.write_function}
        return write_functions_dict[command_type](*args)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()
