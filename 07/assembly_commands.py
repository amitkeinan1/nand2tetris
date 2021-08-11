from .vm_commands import *

assembly = {
    ADD_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M+D"],
    SUB_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M-D"],
    NEG_COMMAND: ["@SP", "A=M", "M=-M"],
    EQ_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "D=M-D", "@{}", "D;JEQ", "D=-1", "@{}", "0:JEQ",
                 "D=0", "@SP", "A=M", "M=D"],
    # TODO
    LT_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M-D"],  # TODO
    GT_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M-D"],  # TODO
    AND_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M&D"],
    OR_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M|D"],
    NOT_COMMAND: ["@SP", "A=M", "M=!M"]

}
