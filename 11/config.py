from enum import Enum


class TokenTypes(Enum):
    KEYWORD = 1
    SYMBOL = 2
    INT_CONST = 3
    STRING_CONST = 4
    IDENTIFIER = 5


SEGMENTS_NAMES = {"CONST": "constant", "ARG": "argument", "LOCAL": "local", "STATIC": "static", "THIS": "this",
                  "THAT": "that", "POINTER": "pointer", "TEMP": "temp"}
