"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from Code import Code
from tables import command_types

COMMENT_SIGN = "//"
C_COMMAND = "C_COMMAND"  # TODO: put in one place


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self._remove_comments_from_lines()
        self._remove_whitespace_lines()
        self.line_index = 0
        self.curr_command = self.input_lines[self.line_index]

    @staticmethod
    def _remove_comments(line: str):
        return line.split(COMMENT_SIGN)[0]

    def _remove_comments_from_lines(self):
        self.input_lines = list(map(self._remove_comments, self.input_lines))

    @staticmethod
    def _is_line_not_whitespace(line: str):
        return line != ''

    def _remove_whitespace_lines(self):
        self.input_lines = list(filter(Parser._is_line_not_whitespace, self.input_lines))

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.line_index < (len(self.input_lines) - 1)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.line_index += 1
        self.curr_command = self.input_lines[self.line_index]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.curr_command[0] in command_types:
            return command_types[self.curr_command[0]]
        else:
            return C_COMMAND

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return self.curr_command[1:]
        else:
            return self.curr_command.strip("()")

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """

        if "=" in self.curr_command:
            dest_symbol = self.curr_command.split("=")[0]
        else:
            dest_symbol = ""
        return Code.dest(dest_symbol)

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        comp = self.curr_command.split("=")[1].split(";")[0]
        return Code.comp(comp)

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if ";" in self.curr_command:
            jump_symbol = self.curr_command.split(";")[1]
        else:
            jump_symbol = ""
        return Code.jump(jump_symbol)
