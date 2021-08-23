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

access_commands = {
    "push": "C_PUSH",
    "pop": "C_POP"
}

branching_commands = {
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if": "C_IF",
    "if-goto": "C_IF",
    "return": "C_RETURN",
    "call": "C_CALL",
    "function": "C_FUNCTION"
}

non_arithmetic_commands = {**access_commands, **branching_commands}

two_args_branching_commands = ["C_CALL", "C_FUNCTION"]
zero_args_branching_commands = ["C_RETURN"]
