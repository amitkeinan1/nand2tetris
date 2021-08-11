arithmetic_commands = ["add", "sub", "neg", "eq", "lt", "gt", "and", "or", "not"]
ARITHMETIC_COMMAND = "C_ARITHMETIC"
non_arithmetic_commands = {
    "push": "C_PUSH",
    "pop": "C_POP",
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if": "C_IF",
    "if-goto": "C_IF",
    "return": "C_RETURN",
    "call": "C_CALL"
}
