from enum import Enum


class TokenTypes(Enum):
    KEYWORD = 1
    SYMBOL = 2
    INT_CONST = 3
    STRING_CONST = 4
    IDENTIFIER = 5
