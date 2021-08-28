"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackPreprocessing import get_tokens
from config import KEY_WORDS, SYMBOLS


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        jack_code = stream.read()
        self.tokens = get_tokens(jack_code)
        self.tokens_num = len(self.tokens)
        self.curr_index = 0
        pass

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.curr_index < self.tokens_num - 1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.curr_index += 1

    @staticmethod
    def _is_string_const(token):
        if len(token) < 2:
            return False
        wrapped_with_double_quotes = token[0] == '"' and token[-1] == '"'
        inner_string = token[1:-1]
        has_inner_double_quotes = '"' in inner_string
        has_inner_new_line = '\n' in inner_string
        return wrapped_with_double_quotes and not (has_inner_double_quotes or has_inner_new_line)

    @staticmethod
    def _is_identifier(token: str):
        if token == "":
            return False
        if token[0].isdigit():
            return False
        for char in token:
            if not (char.isdigit() or char.isalpha() or char == '_'):
                return False
        return True

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        curr_token = self.tokens[self.curr_index]
        if curr_token in KEY_WORDS:
            return "KEYWORD"
        elif curr_token in SYMBOLS:
            return "SYMBOL"
        elif curr_token.isdigit() and 0 <= int(curr_token) <= 32767:
            return "INT_CONST"
        elif JackTokenizer._is_string_const(curr_token):
            return "STRING_CONST"
        elif JackTokenizer._is_identifier(curr_token):
            return "IDENTIFIER"
        else:
            raise Exception(f"token {curr_token} is not valid.")

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.tokens[self.curr_index]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.tokens[self.curr_index]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.tokens[self.curr_index]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.tokens[self.curr_index])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.tokens[self.curr_index][1:-1]


if __name__ == '__main__':
    with open("Square/Main.jack") as stream:
        t = JackTokenizer(stream)
        print(t.tokens[t.curr_index])
        print(t.token_type())
        print()
        while t.has_more_tokens():
            t.advance()
            print(t.tokens[t.curr_index])
            print(t.token_type())
            print()
