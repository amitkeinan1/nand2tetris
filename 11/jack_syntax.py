import re

KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

STRING_CONST_PATTERN = '"[^\\n"]*?"'
IDENTIFIER_PATTERN = '[a-zA-Z_][a-zA-Z0-9_]*'

# comments removing
COMMENTS_REGEX = re.compile(r'//[^\n]*\n|/\*(.*?)\*/', re.MULTILINE | re.DOTALL)

INLINE_COMMENT_REPLACEMENT = "\n"
DEFAULT_REPLACEMENT = ""

OPERATORS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
UNARY_OPERATORS = ['-', '~']
KEYWORD_CONSTANTS = ['true', 'false', 'null', 'this']
