"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing

from CodeWriter import CodeWriter
from Parser import Parser
from vm_commands import ARITHMETIC_COMMAND, access_commands, branching_commands, two_args_branching_commands, zero_args_branching_commands


def translate_file(input_file: typing.TextIO, writer: CodeWriter) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)
    writer.set_file_name(input_filename)
    # writer = CodeWriter(output_file)
    while parser.has_more_commands():
        writer.write_comment_line(fr"// {parser.curr_command}")
        writer.write_line(f"@{666+writer.files_counter}")
        writer.write_line("A=M")
        command_type = parser.command_type()
        if command_type is ARITHMETIC_COMMAND:
            writer.write_arithmetic(parser.curr_command)
        elif command_type in access_commands.values():
            writer.write_push_pop(command_type, parser.arg1(), int(parser.arg2()))
        elif command_type in branching_commands.values():
            if command_type in zero_args_branching_commands:
                writer.write_branching(command_type)
            elif command_type in two_args_branching_commands:
                writer.write_branching(command_type, parser.arg1(), parser.arg2())
            else:
                writer.write_branching(command_type, parser.arg1())
        parser.advance()
    # writer.close()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)
            if filename.endswith(".vm")]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        writer = CodeWriter(output_file)
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, writer)
