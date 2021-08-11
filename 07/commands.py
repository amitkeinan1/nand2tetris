arithmetic_commands = ["add", "sub", "neg", "eq", "lt", "gt", "and", "or", "not"]
ARITHMETIC_COMMAND = "C_ARITHMETIC"
PUSH_COMMAND = "C_PUSH"
POP_COMMAND = "C_POP"
ACCESS_COMMANDS = [PUSH_COMMAND, POP_COMMAND]
non_arithmetic_commands = {
    "push": PUSH_COMMAND,
    "pop": POP_COMMAND,
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if": "C_IF",
    "if-goto": "C_IF",
    "return": "C_RETURN",
    "call": "C_CALL"
}
