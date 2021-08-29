"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re
import typing
from lxml import etree as ET

from JackPreprocessing import get_tokens
from config import KEY_WORDS, SYMBOLS, IDENTIFIER_PATTERN, STRING_CONST_PATTERN


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
        self._type_to_repr_method = {"KEYWORD": self.keyword, "SYMBOL": self.symbol, "INT_CONST": self.int_val,
                                     "STRING_CONST": self.string_val, "IDENTIFIER": self.identifier}

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
        return bool(re.fullmatch(STRING_CONST_PATTERN, token))

    @staticmethod
    def _is_identifier(token: str):
        return bool(re.fullmatch(IDENTIFIER_PATTERN, token))

    def curr_token(self):
        return self.tokens[self.curr_index]

    def token_type(self) -> str:  # TODO rewrite with regexes
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        curr_token = self.curr_token()
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

    def _token_repr(self):
        return str(self._type_to_repr_method[self.token_type()]())

    def tokenize(self, output_path: str) -> None:
        tokens_root = ET.Element("tokens")

        ET.SubElement(tokens_root, self.token_type()).text = self._token_repr()
        while t.has_more_tokens():
            t.advance()
            ET.SubElement(tokens_root, self.token_type()).text = self._token_repr()

        tokens_tree = ET.ElementTree(tokens_root)
        tokens_tree.write(output_path, pretty_print=True)


if __name__ == '__main__':
    with open("TokenizerTest/condition.jack") as stream:
        t = JackTokenizer(stream)
        t.tokenize("tokens.xml")
