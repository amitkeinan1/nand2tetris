from .vm_commands import *

assembly = {
    ADD_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M+D"],  # *(SP-2) = *(SP-2) + *(SP-1)
    SUB_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M-D"],  # *(SP-2) = *(SP-2) - *(SP-1)
    NEG_COMMAND: ["@SP", "A=M", "M=-M"],  # *(SP-1) = -*(SP-1)
    EQ_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "D=M-D",  # D =  # *(SP-2) - *(SP-1)
                 "@{}", "D;JEQ",  # if D==0 jump to curr_line + 2
                 "D=-1",  # D=true
                 "@{}", "0:JEQ",  # skip setting D to false by jumping to curr_line + 2
                 "D=0",  # D=false
                 "@SP", "M=M-1", "A=M", "M=D"  # *(SP-1) = D
                 ],  # TODO
    LT_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "D=M-D",  # D =  # *(SP-2) - *(SP-1)
                 "@{}", "D;JLT",  # if D<0 jump to curr_line + 2
                 "D=-1",  # D=true
                 "@{}", "0:JEQ",  # skip setting D to false by jumping to curr_line + 2
                 "D=0",  # D=false
                 "@SP", "M=M-1", "A=M", "M=D"  # *(SP-1) = D
                 ],  # TODO
    GT_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "D=M-D",  # D =  # *(SP-2) - *(SP-1)
                 "@{}", "D;JGT",  # if D>0 jump to curr_line + 2
                 "D=-1",  # D=true
                 "@{}", "0:JEQ",  # skip setting D to false by jumping to curr_line + 2
                 "D=0",  # D=false
                 "@SP", "M=M-1", "A=M", "M=D"  # *(SP-1) = D
                 ],  # TODO
    AND_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M&D"],  # *(SP-2) = *(SP-2) & *(SP-1)
    OR_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M|D"],  # *(SP-2) = *(SP-2) | *(SP-1)
    NOT_COMMAND: ["@SP", "A=M", "M=!M"]  # *(SP-1) = !*(SP-1)

}
