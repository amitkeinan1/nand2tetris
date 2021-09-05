from ExtendedXmlCompiler import ExtendedXmlCompiler
from CodeWriter import CodeWriter

if __name__ == '__main__':
    file_name = "simple_expression"
    compiler = ExtendedXmlCompiler(file_name + ".jack", file_name + ".xml")
    compiler.compile_expression()
    code_writer = CodeWriter(file_name + ".xml", file_name + ".vm")
    code_writer.write_code()
