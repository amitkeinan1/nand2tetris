KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

STRING_CONST_PATTERN = '"[^\\n"]*?"'
IDENTIFIER_PATTERN = '[a-zA-Z_][a-zA-Z0-9_]*'

# comments removing

INLINE_COMMENT_PATTERN = "//.*\n"
MULTILINE_COMMENT_PATTERN = "\s*/\*\*\n(\s*\*.*\n)*\s*\*/"
API_COMMENT_PATTERN = "/\*\*.*\*/"

INLINE_COMMENT_REPLACEMENT = "\n"
DEFAULT_REPLACEMENT = ""

COMMENTS_REMOVING = {INLINE_COMMENT_PATTERN: INLINE_COMMENT_REPLACEMENT,
                     MULTILINE_COMMENT_PATTERN: DEFAULT_REPLACEMENT,
                     API_COMMENT_PATTERN: DEFAULT_REPLACEMENT}

OPERATORS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
UNARY_OPERATORS = ['-', '~']
KEYWORD_CONSTANTS = ['true', 'false', 'null', 'this']
