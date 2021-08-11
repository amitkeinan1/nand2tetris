from vm_commands import *

arithmetic_commands = {
    ADD_COMMAND: [  # the pseudo-assembly code fo the add operation is: *(SP-2) = *(SP-2) + *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "M=M+D",  # *(SP-1) = *(SP-1)+D
        "@SP", "M=M+1"  # SP++
    ],
    SUB_COMMAND: [  # the pseudo-assembly code fo the sub operation is: *(SP-2) = *(SP-2) - *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "M=M-D",  # *(SP-1) = *(SP-1)-D
        "@SP", "M=M+1"  # SP++
    ],
    NEG_COMMAND: ["@SP", "A=M", "M=-M"],  # *(SP-1) = -*(SP-1)
    EQ_COMMAND: [
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "D=M-D",  # D =  *(SP-1) - D
        "@{}", "D;JEQ",  # if D==0 jump to curr_line + 2
        "D=0",  # D=true
        "@{}", "0;JEQ",  # skip setting D to false by jumping to curr_line + 2
        "D=-1",  # D=false
        "@SP", "A=M", "M=D",  # *(SP-1) = D
        "@SP", "M=M+1"  # SP++
    ],
    LT_COMMAND: ["@SP", "A=M-1", "D=M",  # D = *(SP-1)
                 "M=0",  # *(SP-1)  = 0
                 "@SP", "M=M-1", "M=M-1",  # SP = SP-2
                 "A=M", "D=M-D",  # D =  *(SP-1) - D
                 "@{}", "D;JLT",  # if D<0 jump to curr_line + 2
                 "D=0",  # D=true
                 "@{}", "0;JEQ",  # skip setting D to false by jumping to curr_line + 2
                 "D=-1",  # D=false
                 "@SP", "A=M", "M=D",  # *(SP-1) = D
                 "@SP", "M=M+1"  # SP++
                 ],
    GT_COMMAND: ["@SP", "A=M-1", "D=M",  # D = *(SP-1)
                 "M=0",  # *(SP-1)  = 0
                 "@SP", "M=M-1", "M=M-1",  # SP = SP-2
                 "A=M", "D=M-D",  # D =  *(SP-1) - D
                 "@{}", "D;JGT",  # if D>0 jump to curr_line + 2
                 "D=0",  # D=true
                 "@{}", "0;JEQ",  # skip setting D to false by jumping to curr_line + 2
                 "D=-1",  # D=false
                 "@SP", "A=M", "M=D",  # *(SP-1) = D
                 "@SP", "M=M+1"  # SP++
                 ],
    AND_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M&D"],  # *(SP-2) = *(SP-2) & *(SP-1) #TODO
    OR_COMMAND: ["@SP", "A=M-1", "D=M", "@SP", "M=M-1", "A=M", "M=M|D"],  # *(SP-2) = *(SP-2) | *(SP-1) #TODO
    NOT_COMMAND: ["@SP", "A=M", "M=!M"]  # *(SP-1) = !*(SP-1) #TODO

}
