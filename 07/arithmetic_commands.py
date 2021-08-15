from vm_commands import *

BRANCH_SKIP = 4
assembly_commands = {
    ADD_COMMAND: [  # the pseudo-assembly code fo the add operation is: *(SP-2) = *(SP-2) + *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1) = 0
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
    NEG_COMMAND: ["@SP", "A=M-1", "M=-M"],  # *(SP-1) = -*(SP-1)

    EQ_COMMAND: [  # the pseudo-assembly code fo the sub operation is: *(SP-2) = *(SP-2) == *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "D=M-D",  # D =  *(SP-1) - D
        "@{}", "D;JNE",  # if D!=0 jump to curr_line + 4
        "@result", "M=-1",  # result=true
        "@{}", "D;JEQ",  # if D==0 jump to curr_line + 4
        "@result", "M=0",  # result=false
        "@result", "D=M",  # D=result
        "@SP", "A=M", "M=D",  # *(SP-1) = D
        "@SP", "M=M+1"  # SP++
    ],
    LT_COMMAND: [  # the pseudo-assembly code fo the sub operation is: *(SP-2) = *(SP-2) < *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "D=M-D",  # D =  *(SP-1) - D
        "@{}", "D;JGE",  # if D>=0 jump to curr_line + 4
        "@result", "M=-1",  # result=true
        "@{}", "D;JLT",  # if D<0 jump to curr_line + 4
        "@result", "M=0",  # result=false
        "@result", "D=M",  # D=result
        "@SP", "A=M", "M=D",  # *(SP-1) = D
        "@SP", "M=M+1"  # SP++
    ],
    GT_COMMAND: [  # the pseudo-assembly code fo the add operation is: *(SP-2) = *(SP-2) > *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "D=M-D",  # D =  *(SP-1) - D
        "@{}", "D;JLE",  # if D<=0 jump to curr_line + 4
        "@result", "M=-1",  # result=true
        "@{}", "D;JGT",  # if D>0 jump to curr_line + 4
        "@result", "M=0",  # result=false
        "@result", "D=M",  # D=result
        "@SP", "A=M", "M=D",  # *(SP-1) = D
        "@SP", "M=M+1"  # SP++
    ],
    AND_COMMAND: [  # the pseudo-assembly code fo the add operation is: *(SP-2) = *(SP-2) & *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "M=M&D",  # *(SP-1) = *(SP-1)&D
        "@SP", "M=M+1"  # SP++
    ],
    OR_COMMAND: [  # the pseudo-assembly code fo the add operation is: *(SP-2) = *(SP-2) | *(SP-1)
        "@SP", "A=M-1", "D=M",  # D = *(SP-1)
        "M=0",  # *(SP-1)  = 0
        "@SP", "M=M-1", "M=M-1",  # SP = SP-2
        "A=M", "M=M|D",  # *(SP-1) = *(SP-1)|D
        "@SP", "M=M+1"  # SP++
    ],
    NOT_COMMAND: ["@SP", "A=M-1", "M=!M"]  # *(SP-1) = !*(SP-1)
}
