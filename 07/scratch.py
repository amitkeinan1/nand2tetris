from CodeWriter import CodeWriter

if __name__ == '__main__':
    output_stream = open("C:/Users/gofer/Documents/University/nand2tetris/nand2tetris/07/temp.asm", 'w')
    cw = CodeWriter(output_stream)
    cw.write_push_pop("C_PUSH", "local", 0)
    cw.write_push_pop("C_PUSH", "local", 1)
    cw.write_arithmetic("eq")
