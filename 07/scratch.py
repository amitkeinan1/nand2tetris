from CodeWriter import CodeWriter

if __name__ == '__main__':
    output_stream = open("../../../../../Google Drive/אקדמיה/אקדמיה - סמסטרים מתקדמים/nand/nand2tetris/07/temp.asm", 'w')
    cw = CodeWriter(output_stream)
    cw.write_push_pop("C_PUSH", "local", 0)