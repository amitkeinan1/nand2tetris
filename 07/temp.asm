@0
D=A
@1
D=M+D
@addr
M=D
@addr
A=M
D=M
@0
A=M
M=D
@0
M=M+1
@1
D=A
@1
D=M+D
@addr
M=D
@addr
A=M
D=M
@0
A=M
M=D
@0
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
D=M-D
@40
D;JEQ
D=0
@43
0;JEQ
D=-1
@SP
A=M
M=D
@SP
M=M+1
