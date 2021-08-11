ADD_COMMAND = "add"
SUB_COMMAND = "sub"
NEG_COMMAND = "neg"
EQ_COMMAND = "eq"
LT_COMMAND = "lt"
GT_COMMAND = "gt"
AND_COMMAND = "and"
OR_COMMAND = "or"
NOT_COMMAND = "not"

arithmetic_commands = [ADD_COMMAND,
                       SUB_COMMAND,
                       NEG_COMMAND,
                       EQ_COMMAND,
                       LT_COMMAND,
                       GT_COMMAND,
                       AND_COMMAND,
                       OR_COMMAND,
                       NOT_COMMAND]
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

