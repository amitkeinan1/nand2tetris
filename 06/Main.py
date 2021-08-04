"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

A_COMMAND = "A_COMMAND"
C_COMMAND = "C_COMMAND"
L_COMMAND = "L_COMMAND"


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    symbol_table = SymbolTable()

    parser = Parser(input_file)
    rom_address = 0

    first_iteration = True
    while parser.has_more_commands():
        if first_iteration:
            first_iteration = False
        else:
            parser.advance()

        if parser.command_type() == L_COMMAND:
            symbol_table.add_entry(parser.symbol(), rom_address)
        else:
            rom_address += 1

    input_file.seek(0)
    parser = Parser(input_file)
    translated_lines = []

    first_iteration = True
    while parser.has_more_commands():
        if first_iteration:
            first_iteration = False
        else:
            parser.advance()
        if parser.command_type() == A_COMMAND:
            value = parser.symbol()
            if not value.isnumeric():
                if symbol_table.contains(value):
                    translated_lines.append(parser.curr_command.replace(value, symbol_table.get_address(value)))
                else:
                    symbol_table.add_symbol(value)
            else:
                translated_lines.append(Code.translate_a_command(value))

        elif parser.command_type() == C_COMMAND:
            dest, comp, jump = parser.dest(), parser.comp(), parser.jump()
            translated_lines.append(Code.translate_c_command(dest, comp, jump))

    output_file.writelines(translated_lines)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
