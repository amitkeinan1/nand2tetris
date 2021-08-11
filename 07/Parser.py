"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from .vm_commands import arithmetic_commands, ARITHMETIC_COMMAND, non_arithmetic_commands


COMMENT_SIGN = "//"


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().splitlines()
        self._clean_lines()
        self._remove_whitespace_lines()
        self.line_index = 0
        self.curr_command = self.input_lines[self.line_index]
        pass

    @staticmethod
    def _remove_comments(line: str):
        return line.split(COMMENT_SIGN)[0]

    @staticmethod
    def _trim_spaces(line: str):
        return line.strip()

    @staticmethod
    def _clean_line(line: str):
        """
        remove everything which is not pure code from line
        """
        line = Parser._remove_comments(line)
        line = Parser._trim_spaces(line)
        return line

    def _clean_lines(self):
        self.input_lines = list(map(self._clean_line, self.input_lines))

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
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        curr_command_type = self.curr_command.split(' ')[0]
        if curr_command_type in arithmetic_commands:
            return ARITHMETIC_COMMAND
        else:
            return non_arithmetic_commands[curr_command_type]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() is ARITHMETIC_COMMAND:
            return self.curr_command
        else:
            return self.curr_command.split(' ')[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return self.curr_command.split(' ')[2]
