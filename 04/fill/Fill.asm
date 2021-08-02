// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

@8191 // screen size - 1
D=A

@screensize
M=D

@initialized
M=0

(INIT)
	@i //i=0
	M=0

		
	@SCREEN
	D=A

	@addr // addr = screen's beggining
	M=D

	@initialized // initialized = true
	M=1
	
	@MAIN_LOOP
	0;JMP

(MAIN_LOOP)
	@initialized
	D=M
	@INIT
	D;JEQ // if initialized==false goto INIT
	@KBD
	D=M
	@WHITE
	D;JEQ // if KBD==0 goto WHITE
	@BLACK
	D;JNE // if KBD!=0 goto BLACK

(WHITE)
	@initialized
	M=0
	@i
	D=M
	@screensize
	D=D-M
	@MAIN_LOOP
	D;JGT // if i>screen_size goto MAIN-LOOP
	
	@addr
	A=M
	M=0
	
	@i
	M=M+1 //i++
	@1
	D=A
	@addr
	M=M+D // addr = addr + 1
	@WHITE
	0;JMP
	

	
(BLACK)
	@initialized
	M=0
	@i
	D=M
	@screensize
	D=D-M
	@MAIN_LOOP
	D;JGT // if i>screen_size goto MAIN-LOOP
	
	@addr
	A=M
	M=-1
	
	@i
	M=M+1 //i++
	@1
	D=A
	@addr
	M=D+M // addr = addr + 1
	@BLACK
	0;JMP
	
