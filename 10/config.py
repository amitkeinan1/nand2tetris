KEY_WORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
             'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']


# comments removing

INLINE_COMMENT_REGEX = "//.*\n"
MULTILINE_COMMENT_REGEX = "/\*.*\*/"
API_COMMENT_REGEX = "/\*\*.*\*/"

INLINE_COMMENT_REPLACEMENT = "\n"
DEFAULT_REPLACEMENT = ""

COMMENTS_REMOVING = {INLINE_COMMENT_REGEX: INLINE_COMMENT_REPLACEMENT,
                     MULTILINE_COMMENT_REGEX: DEFAULT_REPLACEMENT,
                     API_COMMENT_REGEX: DEFAULT_REPLACEMENT}