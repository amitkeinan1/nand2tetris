from enum import Enum


class TokenTypes(Enum):
    KEYWORD = 1
    SYMBOL = 2
    INT_CONST = 3
    STRING_CONST = 4
    IDENTIFIER = 5


DEFINITION = "definition"
USAGE = "usage"

SEGMENTS_NAMES = {"CONST": "constant", "ARG": "argument", "LOCAL": "local", "STATIC": "static", "THIS": "this",
                  "THAT": "that", "POINTER": "pointer", "TEMP": "temp"}

VAR_KINDS = {"static": "STATIC", "field": "FIELD", "argument": "ARG", "var": "VAR"}

KIND_TO_SEGMENT = {"STATIC": "STATIC", "FIELD": "THIS", "ARG": "ARG", "VAR": "LOCAL"}


class IdentifierTypes(Enum):
    CLASS_NAME = 1
    CLASS_VAR_NAME = 2
    SUBROUTINE_NAME = 3
    ARGUMENT_NAME = 4
    IDENTIFIER = 5


CLASS_TAG = "class"
CLASS_VAR_DEC_TAG = "classVarDec"
SUBROUTINE_DEC_TAG = "subroutineDec"
PARAMETER_LIST_TAG = "parameterList"
VAR_DEC_TAG = "varDec"
STATEMENTS_TAG = "statements"
DO_TAG = "doStatement"
LET_TAG = "letStatement"
WHILE_TAG = "whileStatement"
RETURN_TAG = "returnStatement"
IF_TAG = "ifStatement"
EXPRESSION_TAG = "expression"
TERM_TAG = "term"
EXPRESSION_LIST_TAG = "expressionList"
SUBROUTINE_TAG = "subroutineBody"
SYMBOL_TAG = "symbol"
INTEGER_CONSTANT_TAG = "integerConstant"
STRING_CONSTANT_TAG = "stringConstant"
KEYWORD_CONSTANT_TAG = "keyword"
op_to_vm_command = {"+": "ADD", "-": "SUB", "=": "EQ", ">": "GT", "<": "LT", "&": "AND",
                    "|": "OR", "!": "NOT"}
op_to_os_function = {"*": "Math.multiply", "/": "Math.divide"}
unary_op_to_vm_command = {"-": "NEG", "~": "NOT"}
