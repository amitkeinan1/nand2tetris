// function SimpleFunction.test 2
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push local 0
@0
D=A
@LCL
D=M+D
@addr
M=D
@addr
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 1
@1
D=A
@LCL
D=M+D
@addr
M=D
@addr
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M+D
@SP
M=M+1
// not
@SP
A=M-1
M=!M
// push argument 0
@0
D=A
@ARG
D=M+D
@addr
M=D
@addr
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M+D
@SP
M=M+1
// push argument 1
@1
D=A
@ARG
D=M+D
@addr
M=D
@addr
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
// return
@0
D=A
@ARG
D=M+D
@addr
M=D
@SP
M=M-1
@SP
A=M
D=M
@addr
A=M
M=D
@LCL
D=M
@FRAME
M=D
@FRAME
D=M
@SP
A=M
M=D
@SP
M=M+1
@5
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
D=M
@RET
M=D
@SP
M=M-1
@ARG
D=M+1
@SP
M=D
@FRAME
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
A=M
D=M
@SP
A=M-1
M=D
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D
@FRAME
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
A=M
D=M
@SP
A=M-1
M=D
@SP
M=M-1
@SP
A=M
D=M
@THIS
M=D
@FRAME
D=M
@SP
A=M
M=D
@SP
M=M+1
@3
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
A=M
D=M
@SP
A=M-1
M=D
@SP
A=M-1
D=M
@ARG
M=D
@SP
M=M-1
@FRAME
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
M=0
@SP
M=M-1
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
A=M
D=M
@SP
A=M-1
M=D
@SP
A=M-1
D=M
@LCL
M=D
@SP
M=M-1
@RET
A=M
0;JMP
